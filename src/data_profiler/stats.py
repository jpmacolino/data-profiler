from __future__ import annotations

from typing import TypedDict

import pandas as pd


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
