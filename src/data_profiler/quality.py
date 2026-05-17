from __future__ import annotations

from typing import TypedDict

import pandas as pd

from data_profiler.inference import infer_column_type


class QualityIssue(TypedDict):
    """A single quality flag raised against a column."""

    column: str
    kind: str
    detail: str


def check_quality(df: pd.DataFrame) -> list[QualityIssue]:
    """Run quality checks against every column in a DataFrame.

    Returns a flat list of QualityIssue dicts in column order. Multiple flags
    can fire on a single column and appear independently in the output. An
    empty DataFrame (zero rows or zero columns) returns an empty list.

    Null-based flags are mutually exclusive per column — only the highest
    applicable tier fires: all_null > almost_entirely_null > mostly_null >
    primarily_null. These thresholds are:
        all_null:              null_count == row_count
        almost_entirely_null:  null_pct >= 0.99
        mostly_null:           null_pct >= 0.90
        primarily_null:        null_pct >= 0.75

    Flags that fire independently of null tiers:
        constant:         >= 99% of non-null values share one value. Does not
                          fire on all-null columns (no non-null values).
        high_cardinality: unique_count / non_null_count >= 0.95. Does not fire
                          on all-null columns.
        mixed_type:       infer_column_type returns 'unknown'.

    Args:
        df: A pandas DataFrame to check.

    Returns:
        A list of QualityIssue dicts, one per (column, kind) pair that fires.
    """
    issues: list[QualityIssue] = []
    row_count = len(df)

    for col in df.columns:
        series = df[col]
        null_count = int(series.isna().sum())
        non_null_count = row_count - null_count

        # --- Null-based flags (mutually exclusive, highest tier only) ---
        # Guarded on row_count > 0 to avoid division by zero and spurious flags
        # on zero-row DataFrames (where null_count == row_count == 0).
        if row_count > 0:
            null_pct = null_count / row_count
            if null_count == row_count:
                issues.append(QualityIssue(
                    column=col,
                    kind="all_null",
                    detail=f"{null_pct * 100:.1f}% null ({null_count:,} of {row_count:,})",
                ))
            elif null_pct >= 0.99:
                issues.append(QualityIssue(
                    column=col,
                    kind="almost_entirely_null",
                    detail=f"{null_pct * 100:.1f}% null ({null_count:,} of {row_count:,})",
                ))
            elif null_pct >= 0.90:
                issues.append(QualityIssue(
                    column=col,
                    kind="mostly_null",
                    detail=f"{null_pct * 100:.1f}% null ({null_count:,} of {row_count:,})",
                ))
            elif null_pct >= 0.75:
                issues.append(QualityIssue(
                    column=col,
                    kind="primarily_null",
                    detail=f"{null_pct * 100:.1f}% null ({null_count:,} of {row_count:,})",
                ))

        # --- Independent flags (only when non-null values exist) ---
        if non_null_count > 0:
            non_null = series.dropna()
            unique_count = int(non_null.nunique())

            # constant: one value accounts for >= 99% of non-null values
            value_counts = non_null.value_counts()
            top_value = value_counts.index[0]
            top_count = int(value_counts.iloc[0])
            top_pct = top_count / non_null_count
            if top_pct >= 0.99:
                issues.append(QualityIssue(
                    column=col,
                    kind="constant",
                    detail=(
                        f"{top_pct * 100:.1f}% of non-null values are"
                        f" '{top_value}' ({top_count:,} of {non_null_count:,})"
                    ),
                ))

            # high_cardinality: unique_count / non_null_count >= 0.95
            cardinality_ratio = unique_count / non_null_count
            if cardinality_ratio >= 0.95:
                issues.append(QualityIssue(
                    column=col,
                    kind="high_cardinality",
                    detail=(
                        f"{cardinality_ratio * 100:.1f}% unique values"
                        f" ({unique_count:,} of {non_null_count:,} non-null)"
                    ),
                ))

        # mixed_type fires regardless of null count or row count
        if infer_column_type(series) == "unknown":
            issues.append(QualityIssue(
                column=col,
                kind="mixed_type",
                detail="could not classify column type",
            ))

    return issues
