# ------------------------ Modules ------------------------
# Libraries =>
import os
import pandas as pd
from dotenv import load_dotenv
# Modules =>
from sql.query.dql.dql_query import DQLQuery
from src.extract.sql_extractor import full_extract
from src.connection.sql_connection import SQLConnection


def read_dates_table(min_id: int, max_id: int) -> pd.DataFrame:
    # ------------------------ .env file ------------------------
    load_dotenv()

    TARGET_DATES_HOST = os.getenv("TARGET_DATES_HOST")
    TARGET_DATES_PORT = int(os.getenv("TARGET_DATES_PORT"))
    TARGET_DATES_USERNAME = os.getenv("TARGET_DATES_USERNAME")
    TARGET_DATES_PASSWORD = os.getenv("TARGET_DATES_PASSWORD")
    TARGET_DATES_DATABASE = os.getenv("TARGET_DATES_DATABASE")
    TARGET_DATES_SCHEMA = os.getenv("TARGET_DATES_SCHEMA")
    TARGET_DATES_TABLE = os.getenv("TARGET_DATES_TABLE")
    TARGET_DATES_PRIMARY_KEY = os.getenv("TARGET_DATES_PRIMARY_KEY")

    # ------------------------ Connection ------------------------
    target_sql_connection = SQLConnection(
        TARGET_DATES_HOST, TARGET_DATES_PORT,
        TARGET_DATES_USERNAME, TARGET_DATES_PASSWORD
    )
    target_sql_connection.connect()
    target_sql_connection.connect()

    # ------------------------ Generate query ------------------------
    dates_dql_query = DQLQuery(TARGET_DATES_DATABASE, TARGET_DATES_SCHEMA, TARGET_DATES_TABLE)
    dates_dql_query.select(["coding_date_id", "display_jalali"])
    condition = dates_dql_query.between("DATES_id", min_id, max_id)
    dates_dql_query.where(condition)
    dates_dql_query = dates_dql_query.build()

    return full_extract(target_sql_connection, dates_dql_query)
