import pandas as pd
from src.connection.sql_connection import SQLConnection


def load(df: pd.DataFrame, connection: SQLConnection, table: str, schema: str) -> None:
    """
    Loads DataFrame into SQL table
    :param df: DataFrame
    :param connection: SQLConnection
    :param table: table name
    :param schema: schema name
    :return: None
    """
    with connection.engine.connect() as connection:
        df.to_sql(name=table, schema=schema, con=connection, if_exists='append', index=False)
