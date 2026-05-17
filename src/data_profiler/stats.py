from __future__ import annotations

from typing import TypedDict

import pandas as pd

from data_profiler.inference import infer_column_type


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


class BooleanStats(TypedDict):
    """Per-column statistics for a boolean Series."""

    true_count: int
    false_count: int
    null_count: int
    unique_count: int


class MinimalStats(TypedDict):
    """Minimal statistics for null or unclassifiable Series."""

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


def _stats_boolean(series: pd.Series) -> BooleanStats:
    """Compute descriptive statistics for a boolean Series.

    Precondition: series is of boolean type and has at least one non-null value.
    inference.py classifies all-null Series as 'null', so callers routing
    through infer_column_type satisfy this invariant automatically. Behavior is
    undefined for non-boolean input.

    Pandas nullable BooleanDtype (pd.BooleanDtype) propagates pd.NA through
    equality comparisons: `series == True` returns pd.NA for NA cells, not
    False. To correctly count True and False values, use `.eq(True).fillna(False)`
    and `.eq(False).fillna(False)` respectively. This avoids incorrect counts
    on nullable boolean columns.

    For object-dtype series inferred as boolean (inference.py allows up to 1%
    non-bool values), any non-bool value that compares equal to True or False
    via `==` (e.g., 1 or 0) will be counted accordingly. This is an accepted
    edge case given the 99% threshold in inference.

    unique_count reflects the number of distinct non-null boolean values (0, 1,
    or 2), following pandas' .nunique() default.
    """
    true_count = int(series.eq(True).fillna(False).sum())
    false_count = int(series.eq(False).fillna(False).sum())
    return BooleanStats(
        true_count=true_count,
        false_count=false_count,
        null_count=int(series.isna().sum()),
        unique_count=int(series.nunique()),
    )


def _stats_minimal(series: pd.Series) -> MinimalStats:
    """Compute minimal statistics for a null or unclassifiable Series.

    Unlike the per-type stats functions, this function has no preconditions:
    it must handle all-null inputs, empty series, and mixed-type series
    correctly. It is the catchall for 'null' and 'unknown' column types.

    unique_count excludes nulls, following pandas' .nunique() default. For
    an all-null or empty series, unique_count is 0.
    """
    return MinimalStats(
        null_count=int(series.isna().sum()),
        unique_count=int(series.nunique()),
    )


def stats_for_column(series: pd.Series) -> NumericStats | StringStats | DatetimeStats | BooleanStats | MinimalStats:
    """Dispatch a Series to the appropriate per-type stats function.

    Infers the column type via infer_column_type, then routes to the matching
    stats function. Returns MinimalStats for 'null' and 'unknown' types.

    Raises ValueError for any col_type not covered by the match arms, which
    makes gaps in coverage observable if ColumnType gains new literals.
    """
    col_type = infer_column_type(series)
    match col_type:
        case "integer" | "float":
            return _stats_numeric(series)
        case "string":
            return _stats_string(series)
        case "datetime":
            return _stats_datetime(series)
        case "boolean":
            return _stats_boolean(series)
        case "null" | "unknown":
            return _stats_minimal(series)
        case _:
            raise ValueError(f"Unhandled column type: {col_type!r}")
