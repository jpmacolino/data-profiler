import math

import pandas as pd
import pytest

from data_profiler.stats import _stats_numeric


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
