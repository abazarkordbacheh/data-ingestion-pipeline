import pandas as pd


def filter_dataframe(
        df: pd.DataFrame,
        column: str,
        values: list[str | int],
        filter_type: str
) -> pd.DataFrame:
    """
    Filter dataframe based on filter_type
    :param df: dataframe
    :param column: column name
    :param values: list of values
    :param filter_type:
        equal            — column value is in values list
        not_equal        — column value is not in values list
        gt               — column > values[0]
        gte              — column >= values[0]
        lt               — column < values[0]
        lte              — column <= values[0]
        between          — values[0] < column < values[1]   (exclusive both ends)
        between_in       — values[0] <= column <= values[1] (inclusive both ends)
        between_out      — column < values[0] OR column > values[1]
        between_gte_lt   — values[0] <= column < values[1]  (inclusive left, exclusive right)
        between_gt_lte   — values[0] < column <= values[1]  (exclusive left, inclusive right)
        :return: filtered dataframe
    """
    if filter_type == "equal":
        return df[df[column].isin(values)]

    if filter_type == "not_equal":
        return df[~df[column].isin(values)]

    if filter_type == "gt":
        return df[df[column] > values[0]]

    if filter_type == "gte":
        return df[df[column] >= values[0]]

    if filter_type == "lt":
        return df[df[column] < values[0]]

    if filter_type == "lte":
        return df[df[column] <= values[0]]

    if filter_type == "between":
        low, high = values[0], values[1]
        return df[(df[column] > low) & (df[column] < high)]

    if filter_type == "between_in":
        low, high = values[0], values[1]
        return df[(df[column] >= low) & (df[column] <= high)]

    if filter_type == "between_out":
        low, high = values[0], values[1]
        return df[(df[column] < low) | (df[column] > high)]

    if filter_type == "between_gte_lt":
        low, high = values[0], values[1]
        return df[(df[column] >= low) & (df[column] < high)]

    if filter_type == "between_gt_lte":
        low, high = values[0], values[1]
        return df[(df[column] > low) & (df[column] <= high)]

    else:
        raise ValueError(f"Unknown filter_type: '{filter_type}'")
