# ------------------------ modules ------------------------
# Libraries =>
import os
import pandas as pd
from dotenv import load_dotenv
# Modules =>
from sql.query.dql.dql_query import DQLQuery
from src.extract.sql_extractor import full_extract
from src.connection.sql_connection import SQLConnection


def read_bank_table(min_id: int, max_id: int) -> pd.DataFrame:
    # ------------------------ .env file ------------------------
    load_dotenv()

    TARGET_BANK_HOST = os.getenv("TARGET_BANK_HOST")
    TARGET_BANK_PORT = int(os.getenv("TARGET_BANK_PORT"))
    TARGET_BANK_USERNAME = os.getenv("TARGET_BANK_USERNAME")
    TARGET_BANK_PASSWORD = os.getenv("TARGET_BANK_PASSWORD")
    TARGET_BANK_DATABASE = os.getenv("TARGET_BANK_DATABASE")
    TARGET_BANK_SCHEMA = os.getenv("TARGET_BANK_SCHEMA")
    TARGET_BANK_TABLE = os.getenv("TARGET_BANK_TABLE")
    TARGET_BANK_PRIMARY_KEY = os.getenv("TARGET_BANK_PRIMARY_KEY")

    # ------------------------ connection ------------------------
    target_sql_connection = SQLConnection(
        TARGET_BANK_HOST, TARGET_BANK_PORT,
        TARGET_BANK_USERNAME, TARGET_BANK_PASSWORD
    )
    target_sql_connection.connect()
    target_sql_connection.connect()

    # ------------------------ Generate query ------------------------
    bank_dql_query = DQLQuery(TARGET_BANK_DATABASE, TARGET_BANK_SCHEMA, TARGET_BANK_TABLE)
    bank_dql_query.select(None)
    condition = bank_dql_query.between("CORESPONDENT_BANK_ID", min_id, max_id)
    bank_dql_query.where(condition)
    bank_dql_query = bank_dql_query.build()

    return full_extract(target_sql_connection, bank_dql_query)
