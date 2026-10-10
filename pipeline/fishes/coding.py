# ------------------------ modules ------------------------
# Libraries =>
import os
import pandas as pd
from dotenv import load_dotenv
# Modules =>
from sql.query.dql.dql_query import DQLQuery
from src.extract.sql_extractor import full_extract
from src.connection.sql_connection import SQLConnection


def read_coding_table() -> pd.DataFrame:
    # ------------------------ .env file ------------------------
    load_dotenv()

    TARGET_CODING_HOST = os.getenv("TARGET_CODING_HOST")
    TARGET_CODING_PORT = int(os.getenv("TARGET_CODING_PORT"))
    TARGET_CODING_USERNAME = os.getenv("TARGET_CODING_USERNAME")
    TARGET_CODING_PASSWORD = os.getenv("TARGET_CODING_PASSWORD")
    TARGET_CODING_DATABASE = os.getenv("TARGET_CODING_DATABASE")
    TARGET_CODING_SCHEMA = os.getenv("TARGET_CODING_SCHEMA")
    TARGET_CODING_TABLE = os.getenv("TARGET_CODING_TABLE")
    TARGET_CODING_PRIMARY_KEY = os.getenv("TARGET_CODING_PRIMARY_KEY")
    # ------------------------ connection ------------------------
    target_sql_connection = SQLConnection(
        TARGET_CODING_HOST, TARGET_CODING_PORT,
        TARGET_CODING_USERNAME, TARGET_CODING_PASSWORD
    )
    target_sql_connection.connect()
    # ------------------------ Generate query ------------------------
    coding_dql_query = DQLQuery(TARGET_CODING_DATABASE, TARGET_CODING_SCHEMA, TARGET_CODING_TABLE)
    coding_dql_query.select(None)
    coding_dql_query = coding_dql_query.build()

    return full_extract(target_sql_connection, coding_dql_query)
