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


@pytest.mark.design_pending
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


def test_boolean_native_dtype():
    series = pd.Series([True, False, True])
    assert infer_column_type(series) == "boolean"


def test_boolean_object_dtype():
    series = pd.Series([True, False, True], dtype=object)
    assert infer_column_type(series) == "boolean"


def test_datetime_native_dtype():
    series = pd.Series(pd.to_datetime(["2024-01-01", "2024-06-15"]))
    assert infer_column_type(series) == "datetime"


def test_datetime_string_coercion():
    series = pd.Series(["2024-01-01", "2024-06-15", "2023-12-31"])
    assert infer_column_type(series) == "datetime"

@pytest.mark.design_pending
@pytest.mark.xfail(reason="Design TBD: should null-induced float coercion preserve integer classification?")
def test_nulls_ignored_for_classification():
    series = pd.Series([1, 2, None, 4])
    assert infer_column_type(series) == "integer"


@pytest.mark.parametrize("bool_count,non_bool_count,expected", [
    (99, 1, "boolean"),   # 99/100 → crosses 99% threshold
    (98, 2, "unknown"),   # 98/100 → just below threshold
])
def test_boolean_threshold(bool_count, non_bool_count, expected):
    values = [True] * bool_count + ["yes"] * non_bool_count
    series = pd.Series(values)
    assert infer_column_type(series) == expected