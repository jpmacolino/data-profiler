# data-profiler

A command-line tool for exploratory data analysis of tabular files — built for the "unfamiliar dataset" moment, not production validation.

> **Status: early development.** The core inference and stats modules are taking shape, but the CLI is a stub and the profiler/report pipeline is not yet wired up.

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

Three private helper functions compute per-column statistics. The public stats API is still in progress.

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

- [ ] CLI argument parsing (`data-profiler <file>`)
- [ ] Profiler orchestration (`profiler.py`)
- [ ] Quality checks (`quality.py`)
- [ ] Report rendering — terminal table and JSON (`report.py`)
- [ ] Public stats API