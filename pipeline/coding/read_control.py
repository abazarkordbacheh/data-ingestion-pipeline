# ------------------------ modules ------------------------

import os
from dotenv import load_dotenv
from sql.query.dql.dql_query import DQLQuery
from src.extract.sql_extractor import get_max_id
from src.connection.sql_connection import SQLConnection

# ------------------------ read_control ------------------------
def read_control():
    # ------------------------ .env file ------------------------
    load_dotenv()

    HOST = os.getenv("CONTROL_CODING_HOST")
    PORT = os.getenv("CONTROL_CODING_PORT")
    USER = os.getenv("CONTROL_CODING_USER")
    PASSWORD = os.getenv("CONTROL_CODING_PASSWORD")
    DATABASE = os.getenv("CONTROL_CODING_DATABASE")
    SCHEMA = os.getenv("CONTROL_CODING_SCHEMA")
    TABLE = os.getenv("CONTROL_CODING_TABLE")
    PRIMARY_KEY = os.getenv("CONTROL_CODING_PRIMARY_KEY")

    # ------------------------ connection ------------------------
    sql_connection = SQLConnection(HOST, int(PORT), USER, PASSWORD, DATABASE)
    sql_connection.connect()

    # ------------------------ Generate query ------------------------
    dql_query = DQLQuery(DATABASE, SCHEMA, TABLE)
    dql_query.select([f"MAX({PRIMARY_KEY})"])
    query = dql_query.query

    # ------------------------ Get max id ------------------------
    max_id = get_max_id(sql_connection,query)

    return max_id
