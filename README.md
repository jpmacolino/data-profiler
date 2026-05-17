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

### Numeric stats scaffold (`stats.py`)

`_stats_numeric(series)` returns a `NumericStats` TypedDict with `mean`, `median`, `std`, `min`, `max`, `null_count`, and `unique_count`. This is a private helper; the public stats API is in progress.

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