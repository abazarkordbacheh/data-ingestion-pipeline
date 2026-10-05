# ------------------------ modules ------------------------

import os
import time

import pandas as pd
import sqlalchemy
from dotenv import load_dotenv
from sql.query.dql.dql_query import DQLQuery
from pipeline.coding.read_control import read_control
from src.connection.sql_connection import SQLConnection
from src.load.loader import load
from src.extract.sql_extractor import extract, get_total_count
from tqdm.auto import tqdm


# ------------------------ final_table ------------------------
def final_table():
    # ------------------------ .env file ------------------------
    load_dotenv()
    # Source =>
    SOURCE_CODING_HOST = os.getenv("SOURCE_CODING_HOST")
    SOURCE_CODING_PORT = int(os.getenv("SOURCE_CODING_PORT"))
    SOURCE_CODING_USERNAME = os.getenv("SOURCE_CODING_USERNAME")
    SOURCE_CODING_PASSWORD = os.getenv("SOURCE_CODING_PASSWORD")
    SOURCE_CODING_DATABASE = os.getenv("SOURCE_CODING_DATABASE")
    SOURCE_CODING_SCHEMA = os.getenv("SOURCE_CODING_SCHEMA")
    SOURCE_CODING_TABLE = os.getenv("SOURCE_CODING_TABLE")
    SOURCE_CODING_PRIMARY_KEY = os.getenv("SOURCE_CODING_PRIMARY_KEY")
    # Target =>
    TARGET_CODING_HOST = os.getenv("TARGET_CODING_HOST")
    TARGET_CODING_PORT = int(os.getenv("TARGET_CODING_PORT"))
    TARGET_CODING_USERNAME = os.getenv("TARGET_CODING_USERNAME")
    TARGET_CODING_PASSWORD = os.getenv("TARGET_CODING_PASSWORD")
    TARGET_CODING_DATABASE = os.getenv("TARGET_CODING_DATABASE")
    TARGET_CODING_SCHEMA = os.getenv("TARGET_CODING_SCHEMA")
    TARGET_CODING_TABLE = os.getenv("TARGET_CODING_TABLE")
    TARGET_CODING_PRIMARY_KEY = os.getenv("TARGET_CODING_PRIMARY_KEY")

    # ------------------------ Get Max ID ------------------------
    # max_id = read_control()
    max_id = 0

    # ------------------------ connection ------------------------
    source_sql_connection = SQLConnection(
        SOURCE_CODING_HOST, SOURCE_CODING_PORT,
        SOURCE_CODING_USERNAME, SOURCE_CODING_PASSWORD,
        SOURCE_CODING_DATABASE, True,
    )

    target_sql_connection = SQLConnection(
        TARGET_CODING_HOST, TARGET_CODING_PORT,
        TARGET_CODING_USERNAME, TARGET_CODING_PASSWORD,
        TARGET_CODING_DATABASE, True,
    )

    source_sql_connection.connect()
    target_sql_connection.connect()

    # ------------------------ Generate query ------------------------
    dql_query = DQLQuery(SOURCE_CODING_DATABASE, SOURCE_CODING_SCHEMA, SOURCE_CODING_TABLE)
    dql_query.select(None)
    conditions = dql_query.greater_than(SOURCE_CODING_PRIMARY_KEY, max_id)
    dql_query.where(conditions)
    query = dql_query.query
    print(query)

    total_dql_query = DQLQuery(SOURCE_CODING_DATABASE, SOURCE_CODING_SCHEMA, SOURCE_CODING_TABLE)
    total_dql_query.select(["COUNT(*)"])
    conditions = total_dql_query.greater_than(SOURCE_CODING_PRIMARY_KEY, max_id)
    total_dql_query.where(conditions)
    total_query = total_dql_query.query
    total_record = get_total_count(source_sql_connection, total_query)

    CHUNK_SIZE = 200
    total_chunks = total_record / CHUNK_SIZE
    for chunk in tqdm(extract(source_sql_connection, query, CHUNK_SIZE),
                      total=int(total_chunks),
                      desc="ETL ► Coding → final_table",
                      colour="white",
                      unit="chunk",
                      unit_scale=False,
                      ncols=100,
                      bar_format=(
                              "{desc}: {percentage:3.0f}%|{bar}| "
                              "{n_fmt}/{total_fmt} chunks "
                              "[{elapsed}<{remaining}, {rate_fmt}]"
                      ),
                      smoothing=0.3):
        print(chunk)
        load(chunk, target_sql_connection, TARGET_CODING_TABLE, TARGET_CODING_SCHEMA)
