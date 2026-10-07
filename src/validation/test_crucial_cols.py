import pytest
import pandas as pd
from src.validation.crucial_cols import filter_all_not_null, filter_any_null


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "name":  ["Ali", "Sara", "Reza", "Mina", "Hossein"],
        "age":   [25,    None,   30,     None,   28],
        "score": [90,    85,     None,   None,   70],
    })


# --- filter_all_not_null ---

def test_all_not_null_returns_only_complete_rows(sample_df):
    result = filter_all_not_null(sample_df, ["age", "score"])
    assert len(result) == 2
    assert set(result["name"]) == {"Ali", "Hossein"}


def test_all_not_null_no_nulls_in_result(sample_df):
    result = filter_all_not_null(sample_df, ["age", "score"])
    assert result["age"].notna().all()
    assert result["score"].notna().all()


def test_all_not_null_single_column(sample_df):
    result = filter_all_not_null(sample_df, ["age"])
    assert len(result) == 3  # Ali, Reza, Hossein


def test_all_not_null_empty_df():
    empty = pd.DataFrame({"age": [], "score": []})
    result = filter_all_not_null(empty, ["age", "score"])
    assert result.empty


def test_all_not_null_no_nulls_at_all():
    df = pd.DataFrame({"age": [1, 2], "score": [3, 4]})
    result = filter_all_not_null(df, ["age", "score"])
    assert len(result) == 2


# --- filter_any_null ---

def test_any_null_returns_rows_with_at_least_one_null(sample_df):
    result = filter_any_null(sample_df, ["age", "score"])
    assert len(result) == 3
    assert set(result["name"]) == {"Sara", "Reza", "Mina"}


def test_any_null_complements_all_not_null(sample_df):
    cols = ["age", "score"]
    complete = filter_all_not_null(sample_df, cols)
    missing = filter_any_null(sample_df, cols)
    assert len(complete) + len(missing) == len(sample_df)


def test_any_null_single_column(sample_df):
    result = filter_any_null(sample_df, ["score"])
    assert len(result) == 2  # Reza, Mina


def test_any_null_empty_df():
    empty = pd.DataFrame({"age": [], "score": []})
    result = filter_any_null(empty, ["age", "score"])
    assert result.empty


def test_any_null_no_nulls_returns_empty():
    df = pd.DataFrame({"age": [1, 2], "score": [3, 4]})
    result = filter_any_null(df, ["age", "score"])
    assert result.empty
