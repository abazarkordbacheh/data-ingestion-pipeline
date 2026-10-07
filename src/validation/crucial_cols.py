import pandas as pd


def filter_all_not_null(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Rows where all given columns have values (none are null)
    :param df: Dataframe
    :param columns: List of column names
    :return: Dataframe
    """
    return df.dropna(subset=columns)


def filter_any_null(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Rows where at least one of the given columns is null
    :param df: Dataframe
    :param columns: List of column names
    :return: Dataframe
    """
    mask = df[columns].isna().any(axis=1)
    return df[mask]
