# ------------------------ modules ------------------------

import os
import time

import pandas as pd
import sqlalchemy
from dotenv import load_dotenv
from sql.query.dql.dql_query import DQLQuery
from pipeline.fishes.read_control import read_control
from src.connection.sql_connection import SQLConnection
from src.extract.sql_extractor import extract, get_total_count
from tqdm.auto import tqdm


# ------------------------ final_table ------------------------

def final_table():
    # ------------------------ .env file ------------------------
    load_dotenv()
    # Source =>
    SOURCE_FISHES_HOST = os.getenv("SOURCE_FISHES_HOST")
    SOURCE_FISHES_PORT = int(os.getenv("SOURCE_FISHES_PORT"))
    SOURCE_FISHES_USERNAME = os.getenv("SOURCE_FISHES_USERNAME")
    SOURCE_FISHES_PASSWORD = os.getenv("SOURCE_FISHES_PASSWORD")
    SOURCE_FISHES_DATABASE = os.getenv("SOURCE_FISHES_DATABASE")
    SOURCE_FISHES_SCHEMA = os.getenv("SOURCE_FISHES_SCHEMA")
    SOURCE_FISHES_TABLE = os.getenv("SOURCE_FISHES_TABLE")
    SOURCE_FISHES_PRIMARY_KEY = os.getenv("SOURCE_FISHES_PRIMARY_KEY")
    # Target =>
    TARGET_FISHES_HOST = os.getenv("TARGET_FISHES_HOST")
    TARGET_FISHES_PORT = int(os.getenv("TARGET_FISHES_PORT"))
    TARGET_FISHES_USERNAME = os.getenv("TARGET_FISHES_USERNAME")
    TARGET_FISHES_PASSWORD = os.getenv("TARGET_FISHES_PASSWORD")
    TARGET_FISHES_DATABASE = os.getenv("TARGET_FISHES_DATABASE")
    TARGET_FISHES_SCHEMA = os.getenv("TARGET_FISHES_SCHEMA")
    TARGET_FISHES_TABLE = os.getenv("TARGET_FISHES_TABLE")
    TARGET_FISHES_PRIMARY_KEY = os.getenv("TARGET_FISHES_PRIMARY_KEY")

    # ------------------------ Get Max ID ------------------------
    max_id = "0"

    # ------------------------ connection ------------------------
    source_sql_connection = SQLConnection(
        SOURCE_FISHES_HOST, SOURCE_FISHES_PORT,
        SOURCE_FISHES_USERNAME, SOURCE_FISHES_PASSWORD
    )

    target_sql_connection = SQLConnection(
        TARGET_FISHES_HOST, TARGET_FISHES_PORT,
        TARGET_FISHES_USERNAME, TARGET_FISHES_PASSWORD
    )

    source_sql_connection.connect()
    target_sql_connection.connect()

    # ------------------------ Generate query ------------------------
    dql_query = DQLQuery(SOURCE_FISHES_DATABASE, SOURCE_FISHES_SCHEMA, SOURCE_FISHES_TABLE)
    dql_query.select(None)
    condition_1 = dql_query.greater_than(SOURCE_FISHES_PRIMARY_KEY, max_id)
    condition_2 = dql_query.equal("IS_MASTER", "1")
    conditions = dql_query.conditions([condition_1, condition_2])
    dql_query.where(conditions)
    query = dql_query.query

    total_dql_query = DQLQuery(SOURCE_FISHES_DATABASE, SOURCE_FISHES_SCHEMA, SOURCE_FISHES_TABLE)
    total_dql_query.select(["COUNT(*)"])
    condition_1 = total_dql_query.greater_than(SOURCE_FISHES_PRIMARY_KEY, max_id)
    condition_2 = total_dql_query.equal("IS_MASTER", "1")
    conditions = total_dql_query.conditions([condition_1, condition_2])
    total_dql_query.where(conditions)
    total_query = total_dql_query.query
    total_record = get_total_count(source_sql_connection,total_query)

    CHUNK_SIZE = 200
    total_chunks = total_record / CHUNK_SIZE
    for chunk in tqdm(extract(source_sql_connection, query, CHUNK_SIZE),
            total=int(total_chunks),
            desc="ETL ► Fishes → final_table",
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
            print("\n")
            print(chunk)
            # pd.merge(chunk,df,"left","")

