from __future__ import annotations

from typing import TypedDict

import pandas as pd

from data_profiler.quality import QualityIssue, check_quality
from data_profiler.stats import (
    BooleanStats,
    DatetimeStats,
    MinimalStats,
    NumericStats,
    StringStats,
    stats_for_column,
)


class ProfileReport(TypedDict):
    """The full profiling result for a DataFrame."""

    row_count: int
    column_count: int
    columns: dict[str, NumericStats | StringStats | DatetimeStats | BooleanStats | MinimalStats]
    quality_issues: list[QualityIssue]


def profile(df: pd.DataFrame) -> ProfileReport:
    """Profile a DataFrame and return a structured report.

    Iterates every column in DataFrame column order, computing per-column
    statistics via stats_for_column. Runs check_quality once across the
    full DataFrame. Assembles and returns a ProfileReport.

    No file I/O or rendering is performed here. The caller is responsible
    for serializing or displaying the result.

    Args:
        df: The DataFrame to profile. May be empty (zero rows or columns).

    Returns:
        A ProfileReport TypedDict with row_count, column_count, a columns
        dict in DataFrame column order, and a quality_issues list.
    """
    columns: dict[str, NumericStats | StringStats | DatetimeStats | BooleanStats | MinimalStats] = {
        col: stats_for_column(df[col]) for col in df.columns
    }
    return ProfileReport(
        row_count=len(df),
        column_count=len(df.columns),
        columns=columns,
        quality_issues=check_quality(df),
    )
