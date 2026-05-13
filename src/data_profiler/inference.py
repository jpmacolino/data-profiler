from __future__ import annotations

from typing import Literal

import pandas as pd

ColumnType = Literal["integer", "float", "boolean", "datetime", "string", "null", "unknown"]

_THRESHOLD = 0.99


def _ratio(mask: pd.Series, total: int) -> float:
    return mask.sum() / total


def _is_int_value(v: object) -> bool:
    if isinstance(v, bool):
        return False
    if isinstance(v, int):
        return True
    if isinstance(v, str):
        try:
            int(v)
            return True
        except ValueError:
            return False
    return False


def _is_float_value(v: object) -> bool:
    if isinstance(v, bool):
        return False
    if isinstance(v, float):
        return True
    if isinstance(v, str):
        try:
            float(v)
            return True
        except ValueError:
            return False
    return False


def infer_column_type(series: pd.Series) -> ColumnType:
    """Infer the semantic type of a pandas Series.

    Null values are ignored when computing type ratios. A column composed
    entirely of nulls is classified as 'null'. All other types require at
    least 99 % of the non-null values to match before the label is applied.
    Types are tested in priority order: null → boolean → integer → float →
    datetime → string → unknown.

    Args:
        series: A pandas Series representing one column of a dataset.

    Returns:
        One of 'null', 'boolean', 'integer', 'float', 'datetime', 'string',
        or 'unknown'.
    """
    non_null = series.dropna()

    if len(non_null) == 0:
        return "null"

    total = len(non_null)

    # Boolean: pandas bool dtype, or object series whose values are all bool
    if pd.api.types.is_bool_dtype(non_null):
        return "boolean"
    if pd.api.types.is_object_dtype(non_null):
        bool_mask = non_null.map(lambda v: isinstance(v, bool))
        if _ratio(bool_mask, total) >= _THRESHOLD:
            return "boolean"

    # Integer: pandas integer dtypes, or object values castable to int (but not float)
    if pd.api.types.is_integer_dtype(non_null):
        return "integer"
    if pd.api.types.is_object_dtype(non_null):
        int_mask = non_null.map(_is_int_value)
        if _ratio(int_mask, total) >= _THRESHOLD:
            return "integer"

    # Float: pandas float dtypes, or object values castable to float (excluding pure ints)
    if pd.api.types.is_float_dtype(non_null):
        return "float"
    if pd.api.types.is_object_dtype(non_null):
        float_mask = non_null.map(_is_float_value)
        if _ratio(float_mask, total) >= _THRESHOLD:
            return "float"

    # Datetime: pandas datetime dtype, or coercible via pd.to_datetime
    if pd.api.types.is_datetime64_any_dtype(non_null):
        return "datetime"
    if pd.api.types.is_object_dtype(non_null) or pd.api.types.is_string_dtype(non_null):
        parsed = pd.to_datetime(non_null, errors="coerce")
        success_ratio = parsed.notna().sum() / total
        if success_ratio >= _THRESHOLD:
            return "datetime"

    # String: object or string dtype (after failing all stricter checks above)
    if pd.api.types.is_object_dtype(non_null) or pd.api.types.is_string_dtype(non_null):
        str_mask = non_null.map(lambda v: isinstance(v, str))
        if _ratio(str_mask, total) >= _THRESHOLD:
            return "string"

    return "unknown"
