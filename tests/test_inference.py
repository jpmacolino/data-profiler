import pandas as pd 
import pytest
from data_profiler.inference import infer_column_type

def test_clean_integer_column(clean_integer_series):
    assert infer_column_type(clean_integer_series) == "integer"


def test_clean_float_column():
    series = pd.Series([1.5, 2.5, 3.5])
    assert infer_column_type(series) == "float"


def test_clean_string_column():
    series = pd.Series(["apple", "banana", "cherry"])
    assert infer_column_type(series) == "string"


def test_all_null_column():
    series = pd.Series([None, None, None])
    assert infer_column_type(series) == "null"


@pytest.mark.xfail(reason="Design TBD: should whole-number floats classify as integer?")
def test_floats_with_no_fractional_part():
    series = pd.Series([1.0, 2.0, 3.0])
    assert infer_column_type(series) == "integer"


@pytest.mark.parametrize("int_count,non_int_count,expected", [
    (50, 50, "unknown"),    # 50/50 → no type hits 99%, falls to unknown
    (90, 10, "unknown"),    # 90/10 → still no type at 99%
    (99, 1, "integer"),     # 99/1 → integers cross threshold
    (98, 2, "unknown"),     # 98/2 → just below int threshold, still unknown
])
def test_integer_threshold(int_count, non_int_count, expected):
    values = [1] * int_count + ["x"] * non_int_count
    series = pd.Series(values)
    assert infer_column_type(series) == expected


def test_integer_threshold_with_float_overlap():
    """98 ints + 2 floats: ints alone fail 99% threshold, but all 100 are float-valid → float"""
    values = [1] * 98 + [1.5, 2.5]
    series = pd.Series(values)
    assert infer_column_type(series) == "float"