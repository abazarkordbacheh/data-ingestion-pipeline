# ------------------------ Modules ------------------------
# Libraries = >
import pandas as pd


# ------------------------ Get Safe Range Data Function ------------------------
def safe_range(series: pd.Series) -> tuple[int, int]:
    """
    Extract safe range from a series.
    Returns the min and max values of a numeric column.
    Returns nothing if there are no valid values.
    :param series: Pandas series
    :return: tuple[int, int] or (0,0)
    """
    valid = pd.to_numeric(series, errors="coerce").dropna()
    if valid.empty:
        return tuple(0, 0)
    return int(valid.min()), int(valid.max())
