from __future__ import annotations

import pandas as pd
import pytest

from data_profiler.profiler import profile, ProfileReport


# ===========================================================================
# Shared small DataFrames
# ===========================================================================

def _make_mixed_df() -> pd.DataFrame:
    """Three columns: integer, string, boolean — five rows each."""
    return pd.DataFrame({
        "age": [10, 20, 30, 40, 50],
        "name": ["alice", "bob", "carol", "dave", "eve"],
        "active": [True, False, True, True, False],
    })


# ===========================================================================
# ProfileReport shape on a small constructed DataFrame
# ===========================================================================

def test_row_count_equals_len_df():
    df = _make_mixed_df()
    result = profile(df)
    assert result["row_count"] == len(df)


def test_column_count_equals_len_df_columns():
    df = _make_mixed_df()
    result = profile(df)
    assert result["column_count"] == len(df.columns)


def test_every_column_name_appears_in_columns_dict():
    df = _make_mixed_df()
    result = profile(df)
    for col in df.columns:
        assert col in result["columns"]


def test_columns_dict_length_matches_dataframe_column_count():
    df = _make_mixed_df()
    result = profile(df)
    assert len(result["columns"]) == len(df.columns)


def test_quality_issues_is_a_list():
    df = _make_mixed_df()
    result = profile(df)
    assert isinstance(result["quality_issues"], list)


# ===========================================================================
# Column order
# ===========================================================================

def test_columns_dict_keys_match_dataframe_column_order():
    df = _make_mixed_df()
    result = profile(df)
    assert list(result["columns"].keys()) == list(df.columns)


# ===========================================================================
# Stats routing (end-to-end)
# ===========================================================================

def test_integer_column_stats_has_mean_key():
    df = _make_mixed_df()
    result = profile(df)
    assert "mean" in result["columns"]["age"]


def test_string_column_stats_has_mode_key():
    df = _make_mixed_df()
    result = profile(df)
    assert "mode" in result["columns"]["name"]


def test_boolean_column_stats_has_true_count_key():
    df = _make_mixed_df()
    result = profile(df)
    assert "true_count" in result["columns"]["active"]


# ===========================================================================
# Quality issues present when expected
# ===========================================================================

def test_all_null_column_produces_non_empty_quality_issues():
    df = pd.DataFrame({
        "good": [1, 2, 3],
        "bad": [None, None, None],
    })
    result = profile(df)
    assert len(result["quality_issues"]) > 0


def test_all_null_column_issue_has_kind_all_null():
    df = pd.DataFrame({
        "good": [1, 2, 3],
        "bad": [None, None, None],
    })
    result = profile(df)
    kinds_for_bad = [
        issue["kind"]
        for issue in result["quality_issues"]
        if issue["column"] == "bad"
    ]
    assert "all_null" in kinds_for_bad


# ===========================================================================
# Quality issues absent when no flags fire
# ===========================================================================

def test_clean_dataframe_quality_issues_is_empty_list():
    # Balanced values, moderate cardinality, no nulls — no flags should fire
    df = pd.DataFrame({
        "country": ["USA", "UK", "France", "Germany", "Spain"] * 4,
        "score": [10, 20, 30, 40, 50] * 4,
    })
    result = profile(df)
    assert result["quality_issues"] == []


# ===========================================================================
# Edge cases
# ===========================================================================

def test_empty_dataframe_row_count_is_zero():
    df = pd.DataFrame()
    result = profile(df)
    assert result["row_count"] == 0


def test_empty_dataframe_column_count_is_zero():
    df = pd.DataFrame()
    result = profile(df)
    assert result["column_count"] == 0


def test_empty_dataframe_columns_dict_is_empty():
    df = pd.DataFrame()
    result = profile(df)
    assert result["columns"] == {}


def test_empty_dataframe_quality_issues_is_empty_list():
    df = pd.DataFrame()
    result = profile(df)
    assert result["quality_issues"] == []


def test_zero_row_dataframe_row_count_is_zero():
    df = pd.DataFrame({
        "x": pd.Series([], dtype="int64"),
        "y": pd.Series([], dtype="object"),
        "z": pd.Series([], dtype="bool"),
    })
    result = profile(df)
    assert result["row_count"] == 0


def test_zero_row_dataframe_column_count_matches():
    df = pd.DataFrame({
        "x": pd.Series([], dtype="int64"),
        "y": pd.Series([], dtype="object"),
        "z": pd.Series([], dtype="bool"),
    })
    result = profile(df)
    assert result["column_count"] == len(df.columns)


def test_zero_row_dataframe_quality_issues_is_empty_list():
    df = pd.DataFrame({
        "x": pd.Series([], dtype="int64"),
        "y": pd.Series([], dtype="object"),
        "z": pd.Series([], dtype="bool"),
    })
    result = profile(df)
    assert result["quality_issues"] == []
