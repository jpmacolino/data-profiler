# data-profiler

A command-line tool for exploratory data analysis of tabular files — built for the "unfamiliar dataset" moment, not production validation.

> **Status: v1.** Type inference, column statistics, quality checks, profiler orchestration, and CLI are all fully implemented. 189 tests pass.

## What's working

### Column type inference (`inference.py`)

`infer_column_type(series: pd.Series) -> ColumnType` classifies a pandas Series into one of seven semantic types:

| Type | Description |
|---|---|
| `null` | All values are null |
| `boolean` | pandas bool dtype, or object series whose values are all `bool` |
| `integer` | pandas integer dtype, or string values castable to `int` (not `float`) |
| `float` | pandas float dtype, or string values castable to `float` |
| `datetime` | pandas datetime dtype, or values coercible via `pd.to_datetime` |
| `string` | object or string dtype after failing all stricter checks |
| `unknown` | does not meet any of the above |

Types are tested in the order listed above. All non-null checks require at least 99% of non-null values to match before the label is applied.

### Column statistics (`stats.py`)

`stats_for_column(series)` is the public dispatcher. It infers the column type via `infer_column_type` and routes to the appropriate per-type stats function, returning one of `NumericStats | StringStats | DatetimeStats | BooleanStats | MinimalStats`.

**`_stats_numeric(series)`** — precondition: series is numeric. Returns a `NumericStats` TypedDict:

| Field | Description |
|---|---|
| `mean` | Arithmetic mean (NaN for all-null series) |
| `median` | Median (NaN for all-null series) |
| `std` | Sample standard deviation, ddof=1 (NaN for all-null series) |
| `min` | Minimum value (NaN for all-null series) |
| `max` | Maximum value (NaN for all-null series) |
| `null_count` | Number of null values |
| `unique_count` | Number of distinct non-null values |

**`_stats_string(series)`** — precondition: series is of string type and has at least one non-null value. Returns a `StringStats` TypedDict:

| Field | Description |
|---|---|
| `min_length` | Shortest string length among non-null values |
| `max_length` | Longest string length among non-null values |
| `mean_length` | Mean string length among non-null values |
| `empty_count` | Count of values that are exactly `""` (length 0); nulls are never counted as empty |
| `mode` | Most frequent non-null value; lexicographically first on ties |
| `mode_count` | Number of times the modal value appears in the series |
| `null_count` | Number of null values |
| `unique_count` | Number of distinct non-null values (nulls excluded, pandas `.nunique()` default) |

**`_stats_datetime(series)`** — precondition: series is of datetime type and has at least one non-null value. Returns a `DatetimeStats` TypedDict:

| Field | Description |
|---|---|
| `min` | Earliest timestamp, skipping nulls |
| `max` | Latest timestamp, skipping nulls |
| `range` | `max - min` as a `pd.Timedelta`; zero when all non-null values are identical |
| `null_count` | Number of null values |
| `unique_count` | Number of distinct non-null values (nulls excluded, pandas `.nunique()` default) |

`min`, `max`, and `range` are not JSON-serializable directly — the caller is responsible for serialization. Timezone information is preserved as-is; the function does not normalize timezones.

**`_stats_boolean(series)`** — precondition: series is of boolean type and has at least one non-null value. Returns a `BooleanStats` TypedDict:

| Field | Description |
|---|---|
| `true_count` | Number of `True` values |
| `false_count` | Number of `False` values |
| `null_count` | Number of null values |
| `unique_count` | Number of distinct non-null boolean values (0, 1, or 2) |

Uses `.eq(True).fillna(False)` to correctly handle nullable `pd.BooleanDtype`, where equality comparisons otherwise propagate `pd.NA`.

**`_stats_minimal(series)`** — no preconditions; handles all-null and empty series. Used as the catchall for `null` and `unknown` column types. Returns a `MinimalStats` TypedDict:

| Field | Description |
|---|---|
| `null_count` | Number of null values |
| `unique_count` | Number of distinct non-null values (0 for all-null or empty series) |

### Quality checks (`quality.py`)

`check_quality(df)` runs quality checks against every column in a DataFrame and returns a flat `list[QualityIssue]` in column order. Multiple flags can fire on a single column.

`QualityIssue` is a TypedDict with three fields: `column` (str), `kind` (str), `detail` (str).

Null-based flags are mutually exclusive per column — only the highest applicable tier fires:

| Kind | Threshold |
|---|---|
| `all_null` | 100% null |
| `almost_entirely_null` | >= 99% null |
| `mostly_null` | >= 90% null |
| `primarily_null` | >= 75% null |

Independent flags fire alongside null tiers when applicable:

| Kind | Condition |
|---|---|
| `constant` | >= 99% of non-null values share one value; does not fire on all-null columns |
| `high_cardinality` | unique_count / non_null_count >= 95%; does not fire on all-null columns |
| `mixed_type` | `infer_column_type` returns `"unknown"` |

An empty DataFrame (zero rows or zero columns) returns an empty list.

### Profiler (`profiler.py`)

`profile(df)` is the single entry point for profiling a DataFrame. It iterates columns in DataFrame order calling `stats_for_column`, runs `check_quality` once across the full DataFrame, and returns a `ProfileReport` TypedDict:

| Field | Type | Description |
|---|---|---|
| `row_count` | `int` | Number of rows in the DataFrame |
| `column_count` | `int` | Number of columns in the DataFrame |
| `columns` | `dict` | Per-column stats in DataFrame column order |
| `quality_issues` | `list[QualityIssue]` | All quality flags, in column order |

No file I/O or rendering is performed by `profile()`. The caller is responsible for serializing or displaying the result.

### CLI (`cli.py`)

```
data-profiler <file> [--format {table,json}] [--input-format {csv,jsonl}] [--output PATH]
```

| Argument | Description |
|---|---|
| `<file>` | Path to the input file (required) |
| `--format` | Output format: `table` (default) or `json` |
| `--input-format` | Override extension-based format detection: `csv` or `jsonl` |
| `--output PATH` | Write output to a file instead of stdout |

Auto-detects input format from extension: `.csv` → `pd.read_csv`, `.jsonl` / `.ndjson` → `pd.read_json(lines=True)`. Prints a helpful message to stderr on missing file or unrecognized extension.

Table output (via rich) renders three sections: Dataset Summary, Column Statistics, and Quality Issues. The Quality Issues section is omitted when there are none.

JSON output is `json.dumps(report, indent=2, default=str)` — a single `ProfileReport` object.

Example invocations:

```
data-profiler data.csv
data-profiler data.csv --format json
data-profiler data.jsonl --format json --output report.json
data-profiler data.csv --input-format csv --format json
```

## Installation

Requires Python 3.11 or later.

```
pip install -e ".[dev]"
```

## Running tests

```
pytest
```

## Roadmap

Deferred for a future release:

- Sampling large files
- Column filtering
- Quiet mode
- `--no-quality` flag to skip quality checks
- File metadata (name, size, modified time) in `ProfileReport`