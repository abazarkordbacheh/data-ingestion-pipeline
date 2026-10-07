# ------------------------ modules ------------------------
# Libraries =>
import os
from dotenv import load_dotenv
# Modules =>
from sql.query.dql.dql_query import DQLQuery
from src.extract.sql_extractor import full_extract
from src.connection.sql_connection import SQLConnection


def read_import_request_table():
    # ------------------------ .env file ------------------------
    load_dotenv()

    TARGET_IMPORT_REQUEST_HOST = os.getenv("TARGET_IMPORT_REQUEST_HOST")
    TARGET_IMPORT_REQUEST_PORT = int(os.getenv("TARGET_IMPORT_REQUEST_PORT"))
    TARGET_IMPORT_REQUEST_USERNAME = os.getenv("TARGET_IMPORT_REQUEST_USERNAME")
    TARGET_IMPORT_REQUEST_PASSWORD = os.getenv("TARGET_IMPORT_REQUEST_PASSWORD")
    TARGET_IMPORT_REQUEST_DATABASE = os.getenv("TARGET_IMPORT_REQUEST_DATABASE")
    TARGET_IMPORT_REQUEST_SCHEMA = os.getenv("TARGET_IMPORT_REQUEST_SCHEMA")
    TARGET_IMPORT_REQUEST_TABLE = os.getenv("TARGET_IMPORT_REQUEST_TABLE")
    TARGET_IMPORT_REQUEST_PRIMARY_KEY = os.getenv("TARGET_IMPORT_REQUEST_PRIMARY_KEY")

    # ------------------------ connection ------------------------
    target_sql_connection = SQLConnection(
        TARGET_IMPORT_REQUEST_HOST, TARGET_IMPORT_REQUEST_PORT,
        TARGET_IMPORT_REQUEST_USERNAME, TARGET_IMPORT_REQUEST_PASSWORD
    )
    target_sql_connection.connect()
    target_sql_connection.connect()

    # ------------------------ Generate query ------------------------
    import_request_dql_query = DQLQuery(TARGET_IMPORT_REQUEST_DATABASE, TARGET_IMPORT_REQUEST_SCHEMA, TARGET_IMPORT_REQUEST_TABLE)
    import_request_dql_query.select(None)
    import_request_dql_query = import_request_dql_query.build()

    return full_extract(target_sql_connection, import_request_dql_query)
