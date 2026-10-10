# ------------------------ modules ------------------------
# Libraries =>
import os
import pandas as pd
from dotenv import load_dotenv
# Modules =>
from sql.query.dql.dql_query import DQLQuery
from src.extract.sql_extractor import full_extract
from src.connection.sql_connection import SQLConnection


def read_branch_table(min_id: int, max_id: int) -> pd.DataFrame:
    # ------------------------ .env file ------------------------
    load_dotenv()

    TARGET_BRANCH_HOST = os.getenv("TARGET_BRANCH_HOST")
    TARGET_BRANCH_PORT = int(os.getenv("TARGET_BRANCH_PORT"))
    TARGET_BRANCH_USERNAME = os.getenv("TARGET_BRANCH_USERNAME")
    TARGET_BRANCH_PASSWORD = os.getenv("TARGET_BRANCH_PASSWORD")
    TARGET_BRANCH_DATABASE = os.getenv("TARGET_BRANCH_DATABASE")
    TARGET_BRANCH_SCHEMA = os.getenv("TARGET_BRANCH_SCHEMA")
    TARGET_BRANCH_TABLE = os.getenv("TARGET_BRANCH_TABLE")
    TARGET_BRANCH_PRIMARY_KEY = os.getenv("TARGET_BRANCH_PRIMARY_KEY")

    # ------------------------ connection ------------------------
    target_sql_connection = SQLConnection(
        TARGET_BRANCH_HOST, TARGET_BRANCH_PORT,
        TARGET_BRANCH_USERNAME, TARGET_BRANCH_PASSWORD
    )
    target_sql_connection.connect()
    target_sql_connection.connect()

    # ------------------------ Generate query ------------------------
    branch_dql_query = DQLQuery(TARGET_BRANCH_DATABASE, TARGET_BRANCH_SCHEMA, TARGET_BRANCH_TABLE)
    branch_dql_query.select(None)
    condition = branch_dql_query.between("BRANCH_ID", min_id, max_id)
    branch_dql_query.where(condition)
    branch_dql_query = branch_dql_query.build()

    return full_extract(target_sql_connection, branch_dql_query)
