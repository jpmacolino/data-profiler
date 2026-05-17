import pandas as pd

from data_profiler.quality import check_quality, QualityIssue


# ===========================================================================
# Helper
# ===========================================================================

def _kinds_for_col(issues: list[QualityIssue], col: str) -> list[str]:
    """Return the list of kind values raised against a specific column."""
    return [issue["kind"] for issue in issues if issue["column"] == col]


# ===========================================================================
# One test per flag kind — DataFrame triggers exactly that flag
# ===========================================================================

def test_all_null_flag_fires():
    df = pd.DataFrame({"col": [None] * 10})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "all_null" in kinds


def test_almost_entirely_null_flag_fires():
    # 99 nulls + 1 non-null in 100 rows → null_pct == 0.99
    values = [None] * 99 + [1]
    df = pd.DataFrame({"col": values})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "almost_entirely_null" in kinds


def test_mostly_null_flag_fires():
    # 91 nulls + 9 non-null in 100 rows → null_pct == 0.91
    values = [None] * 91 + list(range(9))
    df = pd.DataFrame({"col": values})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "mostly_null" in kinds


def test_primarily_null_flag_fires():
    # 76 nulls + 24 non-null in 100 rows → null_pct == 0.76
    values = [None] * 76 + list(range(24))
    df = pd.DataFrame({"col": values})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "primarily_null" in kinds


def test_constant_flag_fires():
    # 100 identical non-null values
    df = pd.DataFrame({"col": ["USA"] * 100})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "constant" in kinds


def test_high_cardinality_flag_fires():
    # all values unique — 100% unique non-null
    df = pd.DataFrame({"col": list(range(100))})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "high_cardinality" in kinds


def test_mixed_type_flag_fires():
    # heterogeneous types → infer_column_type returns 'unknown'
    df = pd.DataFrame({"col": [1, "a", True, 2.5, "b"]})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "mixed_type" in kinds


# ===========================================================================
# Boundary tests at each null threshold
# ===========================================================================

def test_74_9_pct_null_does_not_fire_primarily_null():
    # 749 of 1000 rows null → 74.9%, just below the 75% threshold
    values = [None] * 749 + list(range(251))
    df = pd.DataFrame({"col": values})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "primarily_null" not in kinds


def test_75_0_pct_null_fires_primarily_null():
    # 750 of 1000 rows null → exactly 75%, threshold is >=0.75
    values = [None] * 750 + list(range(250))
    df = pd.DataFrame({"col": values})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "primarily_null" in kinds


def test_89_9_pct_null_fires_primarily_null_not_mostly_null():
    # 899 of 1000 rows null → 89.9%, in primarily_null band
    values = [None] * 899 + list(range(101))
    df = pd.DataFrame({"col": values})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "primarily_null" in kinds
    assert "mostly_null" not in kinds


def test_90_0_pct_null_fires_mostly_null_not_primarily_null():
    # 900 of 1000 rows null → exactly 90%, crosses into mostly_null
    values = [None] * 900 + list(range(100))
    df = pd.DataFrame({"col": values})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "mostly_null" in kinds
    assert "primarily_null" not in kinds


def test_98_9_pct_null_fires_mostly_null_not_almost_entirely_null():
    # 989 of 1000 rows null → 98.9%, still in mostly_null band
    values = [None] * 989 + list(range(11))
    df = pd.DataFrame({"col": values})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "mostly_null" in kinds
    assert "almost_entirely_null" not in kinds


def test_99_0_pct_null_fires_almost_entirely_null_not_mostly_null():
    # 990 of 1000 rows null → exactly 99%, crosses into almost_entirely_null
    values = [None] * 990 + list(range(10))
    df = pd.DataFrame({"col": values})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "almost_entirely_null" in kinds
    assert "mostly_null" not in kinds


def test_100_pct_null_fires_all_null_not_almost_entirely_null():
    # 1000 of 1000 rows null → 100%, fires all_null only
    values = [None] * 1000
    df = pd.DataFrame({"col": values})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "all_null" in kinds
    assert "almost_entirely_null" not in kinds


# ===========================================================================
# Multi-flag test: almost_entirely_null AND constant on the same column
# ===========================================================================

def test_almost_entirely_null_and_constant_both_fire():
    # 990 nulls + 10 identical non-null values in 1000 rows
    values = [None] * 990 + ["X"] * 10
    df = pd.DataFrame({"col": values})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "almost_entirely_null" in kinds
    assert "constant" in kinds


# ===========================================================================
# All-null column: null-tier flags are mutually exclusive
# ===========================================================================

def test_all_null_column_does_not_fire_almost_entirely_null():
    df = pd.DataFrame({"col": [None] * 100})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "almost_entirely_null" not in kinds


def test_all_null_column_does_not_fire_mostly_null():
    df = pd.DataFrame({"col": [None] * 100})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "mostly_null" not in kinds


def test_all_null_column_does_not_fire_primarily_null():
    df = pd.DataFrame({"col": [None] * 100})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "primarily_null" not in kinds


def test_all_null_column_does_not_fire_constant():
    # No non-null values → constant flag must not fire
    df = pd.DataFrame({"col": [None] * 100})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "constant" not in kinds


def test_all_null_column_does_not_fire_high_cardinality():
    # No non-null values → high_cardinality flag must not fire
    df = pd.DataFrame({"col": [None] * 100})
    kinds = _kinds_for_col(check_quality(df), "col")
    assert "high_cardinality" not in kinds


# ===========================================================================
# Edge cases
# ===========================================================================

def test_empty_dataframe_returns_empty_list():
    df = pd.DataFrame()
    assert check_quality(df) == []


def test_zero_row_dataframe_with_columns_returns_empty_list():
    df = pd.DataFrame({"a": pd.Series([], dtype="object"), "b": pd.Series([], dtype="float64")})
    assert check_quality(df) == []


def test_clean_dataframe_no_flags():
    # Balanced mixed values, moderate cardinality, no nulls → no issues expected
    df = pd.DataFrame({
        "country": ["USA", "UK", "France", "Germany", "Spain"] * 20,
        "score": [10, 20, 30, 40, 50] * 20,
    })
    assert check_quality(df) == []


# ===========================================================================
# Column order
# ===========================================================================

def test_issues_returned_in_column_order():
    # col_a has all-null, col_b is clean — issues for col_a must precede col_b
    values_a = [None] * 100
    values_b = list(range(100))
    df = pd.DataFrame({"col_a": values_a, "col_b": values_b})
    issues = check_quality(df)
    col_sequence = [issue["column"] for issue in issues]
    # col_a must appear before col_b in the output
    a_positions = [i for i, c in enumerate(col_sequence) if c == "col_a"]
    b_positions = [i for i, c in enumerate(col_sequence) if c == "col_b"]
    assert a_positions  # col_a must have at least one issue
    assert max(a_positions) < min(b_positions)
