# ------------------------ modules ------------------------
# Libraries =>
import os
import datetime
from tqdm.auto import tqdm
from dotenv import load_dotenv
# Modules =>
from src.load.loader import load
from sql.query.dql.dql_query import DQLQuery
from pipeline.coding.read_control import read_control
from src.connection.sql_connection import SQLConnection
from src.extract.sql_extractor import extract, get_total_count


# ------------------------ final_table ------------------------
def final_table():
    # ------------------------ .env file ------------------------
    load_dotenv()
    # Source =>
    SOURCE_BANK_HOST = os.getenv("BANK_HOST")
    SOURCE_BANK_PORT = int(os.getenv("SOURCE_BANK_PORT"))
    SOURCE_BANK_USERNAME = os.getenv("SOURCE_BANK_USERNAME")
    SOURCE_BANK_PASSWORD = os.getenv("SOURCE_BANK_PASSWORD")
    SOURCE_BANK_DATABASE = os.getenv("SOURCE_BANK_DATABASE")
    SOURCE_BANK_SCHEMA = os.getenv("SOURCE_BANK_SCHEMA")
    SOURCE_BANK_TABLE = os.getenv("SOURCE_BANK_TABLE")
    SOURCE_BANK_PRIMARY_KEY = os.getenv("SOURCE_BANK_PRIMARY_KEY")
    # Target =>
    TARGET_BANK_HOST = os.getenv("TARGET_BANK_HOST")
    TARGET_BANK_PORT = int(os.getenv("TARGET_BANK_PORT"))
    TARGET_BANK_USERNAME = os.getenv("TARGET_BANK_USERNAME")
    TARGET_BANK_PASSWORD = os.getenv("TARGET_BANK_PASSWORD")
    TARGET_BANK_DATABASE = os.getenv("TARGET_BANK_DATABASE")
    TARGET_BANK_SCHEMA = os.getenv("TARGET_BANK_SCHEMA")
    TARGET_BANK_TABLE = os.getenv("TARGET_BANK_TABLE")
    TARGET_BANK_PRIMARY_KEY = os.getenv("TARGET_BANK_PRIMARY_KEY")

    # ------------------------ Get Max ID ------------------------
    # max_id = read_control()
    max_id = 0

    # ------------------------ connection ------------------------
    source_sql_connection = SQLConnection(
        SOURCE_BANK_HOST, SOURCE_BANK_PORT,
        SOURCE_BANK_USERNAME, SOURCE_BANK_PASSWORD,
        SOURCE_BANK_DATABASE, True,
    )

    target_sql_connection = SQLConnection(
        TARGET_BANK_HOST, TARGET_BANK_PORT,
        TARGET_BANK_USERNAME, TARGET_BANK_PASSWORD,
        TARGET_BANK_DATABASE, True,
    )

    source_sql_connection.connect()
    target_sql_connection.connect()

    # ------------------------ Generate query ------------------------
    dql_query = DQLQuery(SOURCE_BANK_DATABASE, SOURCE_BANK_SCHEMA, SOURCE_BANK_TABLE)
    dql_query.select(None)
    conditions = dql_query.greater_than(SOURCE_BANK_PRIMARY_KEY, max_id)
    dql_query.where(conditions)
    query = dql_query.query
    print(query)

    total_dql_query = DQLQuery(SOURCE_BANK_DATABASE, SOURCE_BANK_SCHEMA, SOURCE_BANK_TABLE)
    total_dql_query.select(["COUNT(*)"])
    conditions = total_dql_query.greater_than(SOURCE_BANK_PRIMARY_KEY, max_id)
    total_dql_query.where(conditions)
    total_query = total_dql_query.query
    total_record = get_total_count(source_sql_connection, total_query)

    CHUNK_SIZE = 200
    total_chunks = total_record / CHUNK_SIZE
    for chunk in tqdm(extract(source_sql_connection, query, CHUNK_SIZE),
                      total=int(total_chunks),
                      desc="ETL ► Bank → final_table",
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
        chunk["insert_time2"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        load(chunk, target_sql_connection, TARGET_BANK_TABLE, TARGET_BANK_SCHEMA)
