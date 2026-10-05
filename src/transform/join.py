import pandas as pd


def join_dataframe(
        df_1: pd.DataFrame,
        df_2: pd.DataFrame,
        columns: list[str],
        join_type: str = "inner"
) -> pd.DataFrame:
    """
       Join two DataFrames on a single key column.

       Args:
           df_1 (pd.DataFrame): The left DataFrame.
           df_2 (pd.DataFrame): The right DataFrame.
           columns (list[str]): A two-element list of key column names:
               - columns[0]: key column in df_1
               - columns[1]: key column in df_2
           join_type (str): Type of join to perform. Accepted values:
               - "inner"  : Only rows with matching keys in both DataFrames (default).
               - "outer"  : All rows from both DataFrames; unmatched rows filled with NaN.
               - "left"   : All rows from df_1, matched rows from df_2.
               - "right"  : All rows from df_2, matched rows from df_1.

       Returns:
           pd.DataFrame: The merged result.

       Raises:
           ValueError: If join_type is not one of the accepted values.

       Example:
           >>> result = join_dataframe(
           ...     df_orders,
           ...     df_customers,
           ...     columns=["customer_id", "id"],
           ...     join_type="left"
           ... )
       """
    if join_type == "inner":
        return pd.merge(df_1, df_2, left_on=columns[0], right_on=columns[1], how="inner")
    elif join_type == "outer":
        return pd.merge(df_1, df_2, left_on=columns[0], right_on=columns[1], how="outer")
    elif join_type == "left":
        return pd.merge(df_1, df_2, left_on=columns[0], right_on=columns[1], how="left")
    elif join_type == "right":
        return pd.merge(df_1, df_2, left_on=columns[0], right_on=columns[1], how="right")
    else:
        raise ValueError(f"Unknown join type: '{join_type}'")
