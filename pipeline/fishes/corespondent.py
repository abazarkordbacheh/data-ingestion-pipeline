# ------------------------ modules ------------------------
# Libraries =>
import os
import pandas as pd
from dotenv import load_dotenv
# Modules =>
from sql.query.dql.dql_query import DQLQuery
from src.extract.sql_extractor import full_extract
from src.connection.sql_connection import SQLConnection


def read_corespondent_table(min_id:int, max_id:int)->pd.DataFrame:
    # ------------------------ .env file ------------------------
    load_dotenv()

    TARGET_CORESPONDENT_BANKS_HOST = os.getenv("TARGET_CORESPONDENT_BANKS_HOST")
    TARGET_CORESPONDENT_BANKS_PORT = int(os.getenv("TARGET_CORESPONDENT_BANKS_PORT"))
    TARGET_CORESPONDENT_BANKS_USERNAME = os.getenv("TARGET_CORESPONDENT_BANKS_USERNAME")
    TARGET_CORESPONDENT_BANKS_PASSWORD = os.getenv("TARGET_CORESPONDENT_BANKS_PASSWORD")
    TARGET_CORESPONDENT_BANKS_DATABASE = os.getenv("TARGET_CORESPONDENT_BANKS_DATABASE")
    TARGET_CORESPONDENT_BANKS_SCHEMA = os.getenv("TARGET_CORESPONDENT_BANKS_SCHEMA")
    TARGET_CORESPONDENT_BANKS_TABLE = os.getenv("TARGET_CORESPONDENT_BANKS_TABLE")
    TARGET_CORESPONDENT_BANKS_PRIMARY_KEY = os.getenv("TARGET_CORESPONDENT_BANKS_PRIMARY_KEY")
    # ------------------------ connection ------------------------
    target_sql_connection = SQLConnection(
        TARGET_CORESPONDENT_BANKS_HOST, TARGET_CORESPONDENT_BANKS_PORT,
        TARGET_CORESPONDENT_BANKS_USERNAME, TARGET_CORESPONDENT_BANKS_PASSWORD
    )
    target_sql_connection.connect()
    # ------------------------ Generate query ------------------------
    # CORESPONDENT_BANKS =>
    corespondent_banks_dql_query = DQLQuery(TARGET_CORESPONDENT_BANKS_DATABASE, TARGET_CORESPONDENT_BANKS_SCHEMA,
                                            TARGET_CORESPONDENT_BANKS_TABLE)
    corespondent_banks_dql_query.select(None)
    condition = corespondent_banks_dql_query.between("CODING_ID", min_id, max_id)
    corespondent_banks_dql_query.where(condition)
    corespondent_banks_dql_query = corespondent_banks_dql_query.build()

    return full_extract(target_sql_connection, corespondent_banks_dql_query)
