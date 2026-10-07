from typing import Generator
from src.connection.sql_connection import SQLConnection
import pandas as pd
import sqlalchemy


def full_extract(connection: SQLConnection, query: str) -> pd.DataFrame | None:
    """
    Extract data from SQL Server
    :param connection: SQL connection
    :param query: SQL query
    :param chunk_size: Chunk size
    :return: DataFrames or None
    """
    with connection.engine.connect() as connection:
        result = connection.execute(query).fetchall()
        return pd.DataFrame(result)


def extract(connection: SQLConnection, query: str, chunk_size: int) -> Generator[pd.DataFrame | None]:
    """
    Extract data from SQL Server
    :param connection: SQL connection
    :param query: SQL query
    :param chunk_size: Chunk size
    :return: Generator of DataFrames or None
    """
    with connection.engine.connect().execution_options(stream_results=True, yield_per=chunk_size) as connection:
        result = connection.execute(query)
        columns = result.keys()

        while True:
            rows = result.fetchmany(chunk_size)
            if not rows:
                break
            yield pd.DataFrame.from_records(rows, columns=columns)


def get_max_id(connection: SQLConnection, query: str) -> int:
    """
    Get max id from SQL Server
    :param connection: SQL connection
    :param query: SQL query
    :return: Int max id
    """
    with connection.engine.connect() as connection:
        max_id = int(connection.execute(sqlalchemy.text(query)).fetchone()[0])
        if max_id is None:
            max_id = 0
        return max_id


def get_total_count(connection: SQLConnection, query: str) -> int:
    """
    Get total count from SQL Server
    :param connection: SQL connection
    :param query: SQL query
    :return: Int total count
    """
    with connection.engine.connect() as connection:
        total_count = int(connection.execute(query).fetchone()[0])
        if total_count is None:
            total_count = 0
        return total_count
