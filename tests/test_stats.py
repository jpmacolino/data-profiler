import math

import pandas as pd
import pytest

from data_profiler.stats import (
    _stats_numeric,
    _stats_string,
    _stats_datetime,
    _stats_boolean,
    _stats_minimal,
    stats_for_column,
    BooleanStats,
    MinimalStats,
)


# ---------------------------------------------------------------------------
# Happy path — typical integers
# ---------------------------------------------------------------------------

def test_integer_series_mean():
    series = pd.Series([1, 2, 3, 4, 5])
    result = _stats_numeric(series)
    assert result["mean"] == pytest.approx(3.0)


def test_integer_series_median():
    series = pd.Series([1, 2, 3, 4, 5])
    result = _stats_numeric(series)
    assert result["median"] == pytest.approx(3.0)


def test_integer_series_std():
    series = pd.Series([1, 2, 3, 4, 5])
    result = _stats_numeric(series)
    # ddof=1 sample std of [1,2,3,4,5] = sqrt(2.5)
    assert result["std"] == pytest.approx(math.sqrt(2.5))


def test_integer_series_min():
    series = pd.Series([1, 2, 3, 4, 5])
    result = _stats_numeric(series)
    assert result["min"] == pytest.approx(1.0)


def test_integer_series_max():
    series = pd.Series([1, 2, 3, 4, 5])
    result = _stats_numeric(series)
    assert result["max"] == pytest.approx(5.0)


def test_integer_series_null_count():
    series = pd.Series([1, 2, 3, 4, 5])
    result = _stats_numeric(series)
    assert result["null_count"] == 0


def test_integer_series_unique_count():
    series = pd.Series([1, 2, 3, 4, 5])
    result = _stats_numeric(series)
    assert result["unique_count"] == 5


# ---------------------------------------------------------------------------
# Return-type assertions — guard against numpy scalar leakage
# ---------------------------------------------------------------------------

def test_integer_series_stat_fields_are_python_float():
    series = pd.Series([1, 2, 3, 4, 5])
    result = _stats_numeric(series)
    for field in ("mean", "median", "std", "min", "max"):
        assert isinstance(result[field], float), (
            f"expected plain Python float for '{field}', got {type(result[field])}"
        )


def test_integer_series_count_fields_are_python_int():
    series = pd.Series([1, 2, 3, 4, 5])
    result = _stats_numeric(series)
    for field in ("null_count", "unique_count"):
        assert isinstance(result[field], int), (
            f"expected plain Python int for '{field}', got {type(result[field])}"
        )


# ---------------------------------------------------------------------------
# Happy path — floats with a null
# ---------------------------------------------------------------------------

def test_float_with_null_null_count():
    series = pd.Series([1.0, 2.0, None, 4.0])
    result = _stats_numeric(series)
    assert result["null_count"] == 1


def test_float_with_null_unique_count_excludes_null():
    series = pd.Series([1.0, 2.0, None, 4.0])
    result = _stats_numeric(series)
    # pandas nunique() excludes NaN by default
    assert result["unique_count"] == 3


def test_float_with_null_mean_ignores_null():
    series = pd.Series([1.0, 2.0, None, 4.0])
    result = _stats_numeric(series)
    assert result["mean"] == pytest.approx((1.0 + 2.0 + 4.0) / 3)


def test_float_with_null_median_ignores_null():
    series = pd.Series([1.0, 2.0, None, 4.0])
    result = _stats_numeric(series)
    # median of [1.0, 2.0, 4.0] = 2.0
    assert result["median"] == pytest.approx(2.0)


def test_float_with_null_min_ignores_null():
    series = pd.Series([1.0, 2.0, None, 4.0])
    result = _stats_numeric(series)
    assert result["min"] == pytest.approx(1.0)


def test_float_with_null_max_ignores_null():
    series = pd.Series([1.0, 2.0, None, 4.0])
    result = _stats_numeric(series)
    assert result["max"] == pytest.approx(4.0)


# ---------------------------------------------------------------------------
# Adversarial — all-null Series
# ---------------------------------------------------------------------------

def test_all_null_null_count():
    series = pd.Series([None, None], dtype="float64")
    result = _stats_numeric(series)
    assert result["null_count"] == 2


def test_all_null_unique_count():
    series = pd.Series([None, None], dtype="float64")
    result = _stats_numeric(series)
    assert result["unique_count"] == 0


def test_all_null_mean_is_nan():
    series = pd.Series([None, None], dtype="float64")
    result = _stats_numeric(series)
    assert math.isnan(result["mean"])


def test_all_null_median_is_nan():
    series = pd.Series([None, None], dtype="float64")
    result = _stats_numeric(series)
    assert math.isnan(result["median"])


def test_all_null_std_is_nan():
    series = pd.Series([None, None], dtype="float64")
    result = _stats_numeric(series)
    assert math.isnan(result["std"])


def test_all_null_min_is_nan():
    series = pd.Series([None, None], dtype="float64")
    result = _stats_numeric(series)
    assert math.isnan(result["min"])


def test_all_null_max_is_nan():
    series = pd.Series([None, None], dtype="float64")
    result = _stats_numeric(series)
    assert math.isnan(result["max"])


# ---------------------------------------------------------------------------
# Adversarial — single-element Series
# ---------------------------------------------------------------------------

def test_single_element_std_is_nan():
    series = pd.Series([42.0])
    result = _stats_numeric(series)
    # ddof=1 on n=1 is undefined → pandas returns NaN
    assert math.isnan(result["std"])


def test_single_element_mean_equals_value():
    series = pd.Series([42.0])
    result = _stats_numeric(series)
    assert result["mean"] == pytest.approx(42.0)


def test_single_element_median_equals_value():
    series = pd.Series([42.0])
    result = _stats_numeric(series)
    assert result["median"] == pytest.approx(42.0)


def test_single_element_min_equals_value():
    series = pd.Series([42.0])
    result = _stats_numeric(series)
    assert result["min"] == pytest.approx(42.0)


def test_single_element_max_equals_value():
    series = pd.Series([42.0])
    result = _stats_numeric(series)
    assert result["max"] == pytest.approx(42.0)


def test_single_element_null_count():
    series = pd.Series([42.0])
    result = _stats_numeric(series)
    assert result["null_count"] == 0


def test_single_element_unique_count():
    series = pd.Series([42.0])
    result = _stats_numeric(series)
    assert result["unique_count"] == 1


# ===========================================================================
# _stats_string
# ===========================================================================

# ---------------------------------------------------------------------------
# Happy path — no nulls, varied lengths
# ---------------------------------------------------------------------------

def test_string_no_nulls_length_stats():
    # "a"=1, "bb"=2, "ccc"=3, "bb"=2 → min=1, max=3, mean=2.0
    series = pd.Series(["a", "bb", "ccc", "bb"])
    result = _stats_string(series)
    assert result["min_length"] == 1
    assert result["max_length"] == 3
    assert result["mean_length"] == pytest.approx(2.0)


def test_string_no_nulls_mode_and_mode_count():
    # "bb" appears twice, others once — "bb" is the mode
    series = pd.Series(["a", "bb", "ccc", "bb"])
    result = _stats_string(series)
    assert result["mode"] == "bb"
    assert result["mode_count"] == 2


def test_string_no_nulls_null_and_unique_counts():
    series = pd.Series(["a", "bb", "ccc", "bb"])
    result = _stats_string(series)
    assert result["null_count"] == 0
    assert result["unique_count"] == 3  # "a", "bb", "ccc"


def test_string_no_nulls_empty_count_is_zero():
    series = pd.Series(["a", "bb", "ccc", "bb"])
    result = _stats_string(series)
    assert result["empty_count"] == 0


# ---------------------------------------------------------------------------
# Return-type assertions — guard against numpy scalar leakage
# ---------------------------------------------------------------------------

def test_string_count_fields_are_python_int():
    series = pd.Series(["x", "y", "z"])
    result = _stats_string(series)
    for field in ("min_length", "max_length", "null_count", "unique_count",
                  "empty_count", "mode_count"):
        assert isinstance(result[field], int), (
            f"expected plain Python int for '{field}', got {type(result[field])}"
        )


def test_string_mean_length_is_python_float():
    series = pd.Series(["x", "y", "z"])
    result = _stats_string(series)
    assert isinstance(result["mean_length"], float), (
        f"expected plain Python float for 'mean_length', got {type(result['mean_length'])}"
    )


def test_string_mode_is_python_str():
    series = pd.Series(["x", "y", "y"])
    result = _stats_string(series)
    assert isinstance(result["mode"], str), (
        f"expected plain Python str for 'mode', got {type(result['mode'])}"
    )


# ---------------------------------------------------------------------------
# Nulls mixed in — lengths and counts exclude nulls correctly
# ---------------------------------------------------------------------------

def test_string_with_nulls_null_count():
    series = pd.Series(["hello", None, "world", None])
    result = _stats_string(series)
    assert result["null_count"] == 2


def test_string_with_nulls_length_stats_exclude_nulls():
    # Only "hello" (5) and "world" (5) are non-null
    series = pd.Series(["hello", None, "world", None])
    result = _stats_string(series)
    assert result["min_length"] == 5
    assert result["max_length"] == 5
    assert result["mean_length"] == pytest.approx(5.0)


def test_string_with_nulls_unique_count_excludes_null():
    # nunique() excludes NaN — "hello" and "world" are 2 distinct non-null values
    series = pd.Series(["hello", None, "world", None])
    result = _stats_string(series)
    assert result["unique_count"] == 2


def test_string_with_nulls_mode_is_non_null_value():
    # "hello" appears twice (non-null), None twice; mode should be a non-null string
    series = pd.Series(["hello", None, "hello", None])
    result = _stats_string(series)
    assert result["mode"] == "hello"
    assert result["mode_count"] == 2


def test_string_with_nulls_empty_count_does_not_count_nulls():
    # None is not an empty string — empty_count must remain 0
    series = pd.Series(["hello", None, "world"])
    result = _stats_string(series)
    assert result["empty_count"] == 0


# ---------------------------------------------------------------------------
# Empty strings — counted separately from nulls
# ---------------------------------------------------------------------------

def test_string_empty_string_counted_in_empty_count():
    series = pd.Series(["", "a", "", "bb"])
    result = _stats_string(series)
    assert result["empty_count"] == 2


def test_string_empty_string_contributes_zero_to_min_length():
    # "" has length 0 → min_length should be 0
    series = pd.Series(["", "a", "bb"])
    result = _stats_string(series)
    assert result["min_length"] == 0


def test_string_empty_string_null_count_not_affected():
    # empty strings are NOT nulls
    series = pd.Series(["", "a", ""])
    result = _stats_string(series)
    assert result["null_count"] == 0


def test_string_empty_string_and_null_counted_independently():
    # one empty string, one null — empty_count=1, null_count=1
    series = pd.Series(["", None, "word"])
    result = _stats_string(series)
    assert result["empty_count"] == 1
    assert result["null_count"] == 1


# ---------------------------------------------------------------------------
# Mode tie-breaking — first alphabetical value wins (pandas default)
# ---------------------------------------------------------------------------

def test_string_mode_tie_returns_first_alphabetical():
    # "apple" and "zebra" appear equally — pandas returns the lexicographically
    # first value when counts tie (Series.mode() sorts alphabetically)
    series = pd.Series(["apple", "zebra", "apple", "zebra"])
    result = _stats_string(series)
    assert result["mode"] == "apple"
    assert result["mode_count"] == 2


def test_string_mode_tie_three_way():
    # three values each appear once — mode is the first alphabetically
    series = pd.Series(["mango", "apple", "banana"])
    result = _stats_string(series)
    assert result["mode"] == "apple"
    assert result["mode_count"] == 1


# ---------------------------------------------------------------------------
# Adversarial — single-element Series
# ---------------------------------------------------------------------------

def test_string_single_element_all_stats():
    series = pd.Series(["only"])
    result = _stats_string(series)
    assert result["min_length"] == 4
    assert result["max_length"] == 4
    assert result["mean_length"] == pytest.approx(4.0)
    assert result["empty_count"] == 0
    assert result["mode"] == "only"
    assert result["mode_count"] == 1
    assert result["null_count"] == 0
    assert result["unique_count"] == 1


# ---------------------------------------------------------------------------
# Adversarial — all values unique (unique_count == len of non-null)
# ---------------------------------------------------------------------------

def test_string_all_unique_values():
    series = pd.Series(["alpha", "beta", "gamma", "delta"])
    result = _stats_string(series)
    assert result["unique_count"] == 4
    # mode_count is 1 when every value appears exactly once
    assert result["mode_count"] == 1


def test_string_all_unique_with_nulls_unique_count_excludes_null():
    series = pd.Series(["alpha", "beta", None, "gamma"])
    result = _stats_string(series)
    assert result["unique_count"] == 3
    assert result["null_count"] == 1


# ===========================================================================
# _stats_datetime
# ===========================================================================

# ---------------------------------------------------------------------------
# Happy path — no nulls, native datetime64 dtype
# ---------------------------------------------------------------------------

def test_datetime_no_nulls_min_max_range():
    series = pd.Series(pd.to_datetime(["2023-01-01", "2023-06-15", "2024-01-01"]))
    result = _stats_datetime(series)
    assert result["min"] == pd.Timestamp("2023-01-01")
    assert result["max"] == pd.Timestamp("2024-01-01")
    assert result["range"] == pd.Timestamp("2024-01-01") - pd.Timestamp("2023-01-01")


def test_datetime_no_nulls_null_and_unique_counts():
    series = pd.Series(pd.to_datetime(["2023-01-01", "2023-06-15", "2024-01-01"]))
    result = _stats_datetime(series)
    assert result["null_count"] == 0
    assert result["unique_count"] == 3


# ---------------------------------------------------------------------------
# Return-type assertions — min/max are Timestamps, range is Timedelta
# ---------------------------------------------------------------------------

def test_datetime_min_is_timestamp():
    series = pd.Series(pd.to_datetime(["2023-01-01", "2024-01-01"]))
    result = _stats_datetime(series)
    assert isinstance(result["min"], pd.Timestamp), (
        f"expected pd.Timestamp for 'min', got {type(result['min'])}"
    )


def test_datetime_max_is_timestamp():
    series = pd.Series(pd.to_datetime(["2023-01-01", "2024-01-01"]))
    result = _stats_datetime(series)
    assert isinstance(result["max"], pd.Timestamp), (
        f"expected pd.Timestamp for 'max', got {type(result['max'])}"
    )


def test_datetime_range_is_timedelta():
    series = pd.Series(pd.to_datetime(["2023-01-01", "2024-01-01"]))
    result = _stats_datetime(series)
    assert isinstance(result["range"], pd.Timedelta), (
        f"expected pd.Timedelta for 'range', got {type(result['range'])}"
    )


def test_datetime_count_fields_are_python_int():
    series = pd.Series(pd.to_datetime(["2023-01-01", "2024-01-01"]))
    result = _stats_datetime(series)
    for field in ("null_count", "unique_count"):
        assert isinstance(result[field], int), (
            f"expected plain Python int for '{field}', got {type(result[field])}"
        )


# ---------------------------------------------------------------------------
# Nulls mixed in — min/max/range computed over non-null values only
# ---------------------------------------------------------------------------

def test_datetime_with_nulls_null_count():
    series = pd.Series(pd.to_datetime(["2023-01-01", None, "2024-01-01", None]))
    result = _stats_datetime(series)
    assert result["null_count"] == 2


def test_datetime_with_nulls_min_max_exclude_nulls():
    series = pd.Series(pd.to_datetime(["2023-01-01", None, "2024-01-01", None]))
    result = _stats_datetime(series)
    assert result["min"] == pd.Timestamp("2023-01-01")
    assert result["max"] == pd.Timestamp("2024-01-01")


def test_datetime_with_nulls_range_excludes_nulls():
    series = pd.Series(pd.to_datetime(["2023-01-01", None, "2024-01-01"]))
    result = _stats_datetime(series)
    expected_range = pd.Timestamp("2024-01-01") - pd.Timestamp("2023-01-01")
    assert result["range"] == expected_range


def test_datetime_with_nulls_unique_count_excludes_null():
    series = pd.Series(pd.to_datetime(["2023-01-01", None, "2024-01-01", None]))
    result = _stats_datetime(series)
    assert result["unique_count"] == 2


# ---------------------------------------------------------------------------
# Adversarial — single-element Series
# ---------------------------------------------------------------------------

def test_datetime_single_element_all_stats():
    series = pd.Series(pd.to_datetime(["2024-07-04"]))
    result = _stats_datetime(series)
    assert result["min"] == pd.Timestamp("2024-07-04")
    assert result["max"] == pd.Timestamp("2024-07-04")
    assert result["range"] == pd.Timedelta(0)
    assert result["null_count"] == 0
    assert result["unique_count"] == 1


# ---------------------------------------------------------------------------
# Adversarial — all values unique
# ---------------------------------------------------------------------------

def test_datetime_all_unique_values():
    series = pd.Series(pd.to_datetime([
        "2020-01-01", "2021-03-15", "2022-07-30", "2023-11-11"
    ]))
    result = _stats_datetime(series)
    assert result["unique_count"] == 4


# ---------------------------------------------------------------------------
# Adversarial — duplicate timestamps (unique_count < len)
# ---------------------------------------------------------------------------

def test_datetime_duplicates_unique_count_less_than_len():
    series = pd.Series(pd.to_datetime([
        "2023-01-01", "2023-01-01", "2024-06-01"
    ]))
    result = _stats_datetime(series)
    assert result["unique_count"] == 2
    assert result["null_count"] == 0
    assert result["min"] == pd.Timestamp("2023-01-01")
    assert result["max"] == pd.Timestamp("2024-06-01")


# ===========================================================================
# _stats_boolean
# ===========================================================================

# ---------------------------------------------------------------------------
# Happy path — mix of True/False/null, regular bool dtype
# ---------------------------------------------------------------------------

def test_boolean_mixed_true_count():
    series = pd.Series([True, False, True, None], dtype=object)
    result = _stats_boolean(series)
    assert result["true_count"] == 2


def test_boolean_mixed_false_count():
    series = pd.Series([True, False, True, None], dtype=object)
    result = _stats_boolean(series)
    assert result["false_count"] == 1


def test_boolean_mixed_null_count():
    series = pd.Series([True, False, True, None], dtype=object)
    result = _stats_boolean(series)
    assert result["null_count"] == 1


def test_boolean_mixed_unique_count():
    # True and False are the two distinct non-null values
    series = pd.Series([True, False, True, None], dtype=object)
    result = _stats_boolean(series)
    assert result["unique_count"] == 2


# ---------------------------------------------------------------------------
# Happy path — all-True series
# ---------------------------------------------------------------------------

def test_boolean_all_true_true_count():
    series = pd.Series([True, True, True])
    result = _stats_boolean(series)
    assert result["true_count"] == 3


def test_boolean_all_true_false_count_is_zero():
    series = pd.Series([True, True, True])
    result = _stats_boolean(series)
    assert result["false_count"] == 0


def test_boolean_all_true_null_count_is_zero():
    series = pd.Series([True, True, True])
    result = _stats_boolean(series)
    assert result["null_count"] == 0


def test_boolean_all_true_unique_count():
    series = pd.Series([True, True, True])
    result = _stats_boolean(series)
    assert result["unique_count"] == 1


# ---------------------------------------------------------------------------
# Happy path — all-False series
# ---------------------------------------------------------------------------

def test_boolean_all_false_false_count():
    series = pd.Series([False, False, False])
    result = _stats_boolean(series)
    assert result["false_count"] == 3


def test_boolean_all_false_true_count_is_zero():
    series = pd.Series([False, False, False])
    result = _stats_boolean(series)
    assert result["true_count"] == 0


def test_boolean_all_false_null_count_is_zero():
    series = pd.Series([False, False, False])
    result = _stats_boolean(series)
    assert result["null_count"] == 0


def test_boolean_all_false_unique_count():
    series = pd.Series([False, False, False])
    result = _stats_boolean(series)
    assert result["unique_count"] == 1


# ---------------------------------------------------------------------------
# Adversarial — nullable BooleanDtype with pd.NA
# ---------------------------------------------------------------------------

def test_boolean_nullable_dtype_true_count():
    # pd.NA must not be counted as True — .eq(True).fillna(False) prevents NA propagation
    series = pd.Series(pd.array([True, False, pd.NA], dtype="boolean"))
    result = _stats_boolean(series)
    assert result["true_count"] == 1


def test_boolean_nullable_dtype_false_count():
    series = pd.Series(pd.array([True, False, pd.NA], dtype="boolean"))
    result = _stats_boolean(series)
    assert result["false_count"] == 1


def test_boolean_nullable_dtype_null_count():
    # pd.NA must be recognised as null
    series = pd.Series(pd.array([True, False, pd.NA], dtype="boolean"))
    result = _stats_boolean(series)
    assert result["null_count"] == 1


def test_boolean_nullable_dtype_unique_count():
    # nunique() excludes pd.NA — True and False are the two distinct values
    series = pd.Series(pd.array([True, False, pd.NA], dtype="boolean"))
    result = _stats_boolean(series)
    assert result["unique_count"] == 2


def test_boolean_nullable_dtype_multiple_nas_null_count():
    # Ensure every pd.NA element is counted, not just the first
    series = pd.Series(pd.array([True, pd.NA, pd.NA, pd.NA], dtype="boolean"))
    result = _stats_boolean(series)
    assert result["null_count"] == 3
    assert result["true_count"] == 1
    assert result["false_count"] == 0


# ---------------------------------------------------------------------------
# Adversarial — regular bool dtype (no nulls)
# ---------------------------------------------------------------------------

def test_boolean_regular_bool_dtype_no_nulls_counts():
    series = pd.Series([True, False, True, False, True], dtype=bool)
    result = _stats_boolean(series)
    assert result["true_count"] == 3
    assert result["false_count"] == 2
    assert result["null_count"] == 0


def test_boolean_regular_bool_dtype_unique_count():
    series = pd.Series([True, False, True, False, True], dtype=bool)
    result = _stats_boolean(series)
    assert result["unique_count"] == 2


# ---------------------------------------------------------------------------
# Adversarial — single-element series (True)
# ---------------------------------------------------------------------------

def test_boolean_single_true_true_count():
    series = pd.Series([True])
    result = _stats_boolean(series)
    assert result["true_count"] == 1


def test_boolean_single_true_false_count_is_zero():
    series = pd.Series([True])
    result = _stats_boolean(series)
    assert result["false_count"] == 0


def test_boolean_single_true_null_count_is_zero():
    series = pd.Series([True])
    result = _stats_boolean(series)
    assert result["null_count"] == 0


def test_boolean_single_true_unique_count():
    series = pd.Series([True])
    result = _stats_boolean(series)
    assert result["unique_count"] == 1


# ---------------------------------------------------------------------------
# Return-type assertions — guard against numpy scalar leakage
# ---------------------------------------------------------------------------

def test_boolean_count_fields_are_python_int():
    series = pd.Series([True, False, True])
    result = _stats_boolean(series)
    for field in ("true_count", "false_count", "null_count", "unique_count"):
        assert isinstance(result[field], int), (
            f"expected plain Python int for '{field}', got {type(result[field])}"
        )


# ===========================================================================
# _stats_minimal
# ===========================================================================

# ---------------------------------------------------------------------------
# Happy path — all-null series
# ---------------------------------------------------------------------------

def test_minimal_all_null_null_count():
    series = pd.Series([None, None], dtype="object")
    result = _stats_minimal(series)
    assert result["null_count"] == 2


def test_minimal_all_null_unique_count_is_zero():
    series = pd.Series([None, None], dtype="object")
    result = _stats_minimal(series)
    assert result["unique_count"] == 0


# ---------------------------------------------------------------------------
# Adversarial — empty series
# ---------------------------------------------------------------------------

def test_minimal_empty_series_null_count_is_zero():
    series = pd.Series([], dtype="object")
    result = _stats_minimal(series)
    assert result["null_count"] == 0


def test_minimal_empty_series_unique_count_is_zero():
    series = pd.Series([], dtype="object")
    result = _stats_minimal(series)
    assert result["unique_count"] == 0


# ---------------------------------------------------------------------------
# Adversarial — single non-null value
# ---------------------------------------------------------------------------

def test_minimal_single_value_null_count_is_zero():
    series = pd.Series(["only"])
    result = _stats_minimal(series)
    assert result["null_count"] == 0


def test_minimal_single_value_unique_count():
    series = pd.Series(["only"])
    result = _stats_minimal(series)
    assert result["unique_count"] == 1


# ---------------------------------------------------------------------------
# Adversarial — mixed-type series (object dtype with heterogeneous values)
# ---------------------------------------------------------------------------

def test_minimal_mixed_type_null_count():
    series = pd.Series([1, "a", True])
    result = _stats_minimal(series)
    assert result["null_count"] == 0


def test_minimal_mixed_type_unique_count():
    # True == 1 in Python, so avoid mixing bools with ints; use distinct-valued types
    series = pd.Series([1, "a", 2.5])
    result = _stats_minimal(series)
    assert result["unique_count"] == 3


# ---------------------------------------------------------------------------
# Return-type assertions — guard against numpy scalar leakage
# ---------------------------------------------------------------------------

def test_minimal_count_fields_are_python_int():
    series = pd.Series([None, None], dtype="object")
    result = _stats_minimal(series)
    for field in ("null_count", "unique_count"):
        assert isinstance(result[field], int), (
            f"expected plain Python int for '{field}', got {type(result[field])}"
        )


# ===========================================================================
# stats_for_column — routing
# ===========================================================================

# ---------------------------------------------------------------------------
# Happy path — integer series → NumericStats
# ---------------------------------------------------------------------------

def test_stats_for_column_integer_returns_numeric_stats():
    series = pd.Series([1, 2, 3, 4, 5])
    result = stats_for_column(series)
    assert "mean" in result


def test_stats_for_column_integer_mean_value():
    series = pd.Series([1, 2, 3, 4, 5])
    result = stats_for_column(series)
    assert result["mean"] == pytest.approx(3.0)


# ---------------------------------------------------------------------------
# Happy path — float series → NumericStats
# ---------------------------------------------------------------------------

def test_stats_for_column_float_returns_numeric_stats():
    series = pd.Series([1.1, 2.2, 3.3])
    result = stats_for_column(series)
    assert "mean" in result


def test_stats_for_column_float_min_value():
    series = pd.Series([1.1, 2.2, 3.3])
    result = stats_for_column(series)
    assert result["min"] == pytest.approx(1.1)


# ---------------------------------------------------------------------------
# Happy path — string series → StringStats
# ---------------------------------------------------------------------------

def test_stats_for_column_string_returns_string_stats():
    series = pd.Series(["apple", "banana", "apple"])
    result = stats_for_column(series)
    assert "mode" in result


def test_stats_for_column_string_mode_value():
    series = pd.Series(["apple", "banana", "apple"])
    result = stats_for_column(series)
    assert result["mode"] == "apple"


# ---------------------------------------------------------------------------
# Happy path — datetime series → DatetimeStats
# ---------------------------------------------------------------------------

def test_stats_for_column_datetime_returns_datetime_stats():
    series = pd.Series(pd.to_datetime(["2023-01-01", "2024-01-01"]))
    result = stats_for_column(series)
    assert "range" in result


def test_stats_for_column_datetime_range_value():
    series = pd.Series(pd.to_datetime(["2023-01-01", "2024-01-01"]))
    result = stats_for_column(series)
    expected = pd.Timestamp("2024-01-01") - pd.Timestamp("2023-01-01")
    assert result["range"] == expected


# ---------------------------------------------------------------------------
# Happy path — boolean series → BooleanStats (not MinimalStats)
# ---------------------------------------------------------------------------

def test_stats_for_column_boolean_returns_boolean_stats():
    series = pd.Series([True, False, True])
    result = stats_for_column(series)
    # BooleanStats has "true_count"; MinimalStats does not
    assert "true_count" in result


def test_stats_for_column_boolean_is_boolean_stats_type():
    # Verify the returned dict has exactly the BooleanStats keys, not MinimalStats keys
    series = pd.Series([True, False, True])
    result = stats_for_column(series)
    assert set(result.keys()) == {"true_count", "false_count", "null_count", "unique_count"}


def test_stats_for_column_boolean_true_count():
    series = pd.Series([True, False, True])
    result = stats_for_column(series)
    assert result["true_count"] == 2


# ---------------------------------------------------------------------------
# Adversarial — all-null series → MinimalStats
# ---------------------------------------------------------------------------

def test_stats_for_column_all_null_returns_minimal_stats():
    series = pd.Series([None, None], dtype="object")
    result = stats_for_column(series)
    # MinimalStats has only null_count and unique_count
    assert set(result.keys()) == {"null_count", "unique_count"}


def test_stats_for_column_all_null_null_count():
    series = pd.Series([None, None], dtype="object")
    result = stats_for_column(series)
    assert result["null_count"] == 2


def test_stats_for_column_all_null_unique_count():
    series = pd.Series([None, None], dtype="object")
    result = stats_for_column(series)
    assert result["unique_count"] == 0


# ---------------------------------------------------------------------------
# Adversarial — unknown/mixed-type series → MinimalStats
# ---------------------------------------------------------------------------

def test_stats_for_column_mixed_type_returns_minimal_stats():
    # A series with heterogeneous non-string values is classified as 'unknown'
    # by infer_column_type — triggers the MinimalStats fallback
    series = pd.Series([1, "a", object()])
    result = stats_for_column(series)
    assert set(result.keys()) == {"null_count", "unique_count"}


def test_stats_for_column_mixed_type_null_count_is_zero():
    series = pd.Series([1, "a", object()])
    result = stats_for_column(series)
    assert result["null_count"] == 0
