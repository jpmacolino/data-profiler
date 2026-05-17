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

    Precondition: series is of string type and has at least one non-null value.
    inference.py classifies all-null Series as 'null', so callers routing
    through infer_column_type satisfy this invariant automatically. Behavior is
    undefined for non-string input.

    Length statistics (min_length, max_length, mean_length) are computed over
    non-null values only; str.len() returns NaN for nulls, which pandas
    skipna=True (the default) handles transparently.

    empty_count counts values that are exactly "" (length 0). Null values are
    never counted as empty — a null is absent, not an empty string.

    mode returns the most frequent non-null value, using the lexicographically
    first value when multiple values tie, matching pandas' Series.mode() sort
    order. mode_count is the number of times that modal value appears in the
    series (including across both null and non-null positions, but mode can
    never be null, so mode_count is always >= 1).

    unique_count excludes nulls, following pandas' .nunique() default.
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

    Precondition: series is of datetime type and has at least one non-null
    value. inference.py classifies all-null Series as 'null', so callers
    routing through infer_column_type satisfy this invariant automatically.
    Behavior is undefined for non-datetime input.

    min and max skip nulls (pandas default). Because the precondition
    guarantees at least one non-null value, both are always defined — an
    all-null series cannot reach this function.

    range is max - min as a pd.Timedelta, representing the wall-clock distance
    from the earliest to the latest timestamp. It is zero when all non-null
    values are identical.

    Timezone information is preserved as-is. If the series is timezone-aware,
    min, max, and range reflect that timezone; the function makes no attempt
    to normalize or convert timezones.

    min, max, and range are not JSON-serializable directly — the caller is
    responsible for serialization.

    unique_count excludes nulls, following pandas' .nunique() default.
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
