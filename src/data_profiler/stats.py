from __future__ import annotations

from typing import TypedDict

import pandas as pd


class StringStats(TypedDict):
    """Per-column statistics for a string Series."""

    min_length: int
    max_length: int
    mean_length: float
    empty_count: int
    mode: str
    mode_count: int
    null_count: int
    unique_count: int


class DatetimeStats(TypedDict):
    """Per-column statistics for a datetime Series."""

    min: pd.Timestamp
    max: pd.Timestamp
    range: pd.Timedelta
    null_count: int
    unique_count: int


class NumericStats(TypedDict):
    """Per-column statistics for a numeric Series."""

    mean: float
    median: float
    std: float
    min: float
    max: float
    null_count: int
    unique_count: int


def _stats_numeric(series: pd.Series) -> NumericStats:
    """Compute descriptive statistics for a numeric Series.

    Assumes the caller has verified the Series is numeric. Behavior is
    undefined for non-numeric input.

    For an all-null Series, mean/median/std/min/max return NaN; the caller
    is responsible for handling NaN in serialization.

    std uses sample standard deviation (ddof=1).
    """
    return NumericStats(
        mean=float(series.mean()),
        median=float(series.median()),
        std=float(series.std()),
        min=float(series.min()),
        max=float(series.max()),
        null_count=int(series.isna().sum()),
        unique_count=int(series.nunique()),
    )


def _stats_string(series: pd.Series) -> StringStats:
    """Compute descriptive statistics for a string Series.

    Precondition: series has at least one non-null value. inference.py
    classifies all-null Series as 'null', so callers routing through
    infer_column_type satisfy this invariant automatically.

    Assumes the caller has verified the Series is of string type. Behavior
    is undefined for non-string input.

    Length statistics are computed over non-null values; str.len() returns
    NaN for nulls which pandas skipna=True (the default) handles transparently.

    mode returns the lexicographically first value when multiple values tie,
    matching pandas' Series.mode() sort order.
    """
    lengths = series.str.len()
    mode_val = series.mode()[0]
    return StringStats(
        min_length=int(lengths.min()),
        max_length=int(lengths.max()),
        mean_length=float(lengths.mean()),
        empty_count=int(series.str.len().eq(0).sum()),
        mode=str(mode_val),
        mode_count=int((series == mode_val).fillna(False).sum()),
        null_count=int(series.isna().sum()),
        unique_count=int(series.nunique()),
    )


def _stats_datetime(series: pd.Series) -> DatetimeStats:
    """Compute descriptive statistics for a datetime Series.

    Precondition: series has at least one non-null value. inference.py
    classifies all-null Series as 'null', so callers routing through
    infer_column_type satisfy this invariant automatically.

    Assumes the caller has verified the Series is of datetime type. Behavior
    is undefined for non-datetime input.

    min/max use pandas' default skipna=True behavior. range is max - min and
    will be a pd.Timedelta.

    Caller is responsible for handling pd.Timestamp and pd.Timedelta in
    serialization — these types are not JSON-serializable directly.
    """
    min_val = pd.Timestamp(series.min())
    max_val = pd.Timestamp(series.max())
    return DatetimeStats(
        min=min_val,
        max=max_val,
        range=max_val - min_val,
        null_count=int(series.isna().sum()),
        unique_count=int(series.nunique()),
    )
