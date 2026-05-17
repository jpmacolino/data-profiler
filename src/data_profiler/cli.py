from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd
from rich import box
from rich.console import Console
from rich.table import Table

from data_profiler.profiler import ProfileReport, profile


def _load_dataframe(path: Path, input_format: str | None) -> pd.DataFrame:
    """Load a DataFrame from a file, auto-detecting format from extension.

    Supports CSV (.csv) and newline-delimited JSON (.jsonl, .ndjson).
    Pass input_format to override extension-based detection; valid values
    are 'csv' and 'jsonl'. Prints a helpful message and exits on failure.
    """
    fmt = input_format
    if fmt is None:
        suffix = path.suffix.lower()
        if suffix == ".csv":
            fmt = "csv"
        elif suffix in {".jsonl", ".ndjson"}:
            fmt = "jsonl"
        else:
            print(
                f"error: unrecognized file extension '{path.suffix}'. "
                f"Use --input-format {{csv,jsonl}} to specify the format.",
                file=sys.stderr,
            )
            sys.exit(1)

    try:
        if fmt == "csv":
            return pd.read_csv(path)
        return pd.read_json(path, lines=True)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        print(f"error: could not read '{path}': {exc}", file=sys.stderr)
        sys.exit(1)


def _col_type_label(stats: dict[str, Any]) -> str:
    """Derive a display type label by inspecting which keys are present."""
    if "mean" in stats:
        return "numeric"
    if "mode" in stats:
        return "string"
    if "range" in stats:
        return "datetime"
    if "true_count" in stats:
        return "boolean"
    return "null/unknown"


def _col_summary(stats: dict[str, Any]) -> str:
    """Return a short human-readable summary stat for a column."""
    if "mean" in stats:
        return f"mean={stats['mean']:.4g}  min={stats['min']:.4g}  max={stats['max']:.4g}"
    if "mode" in stats:
        return f"mode='{stats['mode']}' ({stats['mode_count']}x)"
    if "range" in stats:
        return f"{stats['min']} — {stats['max']}"
    if "true_count" in stats:
        return f"true={stats['true_count']}  false={stats['false_count']}"
    return ""


def _render_table(report: ProfileReport, console: Console) -> None:
    """Render a ProfileReport as rich terminal tables (three sections).

    Sections: dataset summary, per-column statistics, quality issues.
    The quality issues section is omitted when the list is empty.
    """
    # Dataset summary
    summary = Table(title="Dataset Summary", box=box.SIMPLE, show_header=False)
    summary.add_column("Metric", style="bold cyan")
    summary.add_column("Value")
    summary.add_row("Rows", f"{report['row_count']:,}")
    summary.add_row("Columns", f"{report['column_count']:,}")
    console.print(summary)

    # Per-column statistics
    col_table = Table(title="Column Statistics", box=box.SIMPLE)
    col_table.add_column("Column", style="bold")
    col_table.add_column("Type", style="dim")
    col_table.add_column("Nulls", justify="right")
    col_table.add_column("Unique", justify="right")
    col_table.add_column("Summary")

    for col_name, stats in report["columns"].items():
        col_table.add_row(
            col_name,
            _col_type_label(stats),
            str(stats["null_count"]),
            str(stats["unique_count"]),
            _col_summary(stats),
        )

    console.print(col_table)

    # Quality issues (section omitted when list is empty)
    if report["quality_issues"]:
        issue_table = Table(title="Quality Issues", box=box.SIMPLE)
        issue_table.add_column("Column", style="bold")
        issue_table.add_column("Kind", style="yellow")
        issue_table.add_column("Detail")
        for issue in report["quality_issues"]:
            issue_table.add_row(issue["column"], issue["kind"], issue["detail"])
        console.print(issue_table)


def main() -> None:
    """Entry point for the data-profiler CLI.

    Also callable as `python -m data_profiler.cli` via the __name__ guard below.
    """
    parser = argparse.ArgumentParser(
        prog="data-profiler",
        description="Profile a tabular dataset for exploratory data analysis.",
    )
    parser.add_argument("file", help="Path to the input file.")
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        dest="output_format",
        help="Output format (default: table).",
    )
    parser.add_argument(
        "--input-format",
        choices=["csv", "jsonl"],
        default=None,
        dest="input_format",
        help="Override extension-based format detection.",
    )
    parser.add_argument(
        "--output",
        default=None,
        dest="output_path",
        metavar="PATH",
        help="Write output to a file instead of stdout.",
    )

    args = parser.parse_args()
    path = Path(args.file)

    if not path.exists():
        print(f"error: file not found: '{path}'", file=sys.stderr)
        sys.exit(1)

    df = _load_dataframe(path, args.input_format)
    report = profile(df)

    if args.output_format == "json":
        output = json.dumps(report, indent=2, default=str)
        if args.output_path:
            Path(args.output_path).write_text(output, encoding="utf-8")
        else:
            print(output)
    else:
        if args.output_path:
            with open(args.output_path, "w", encoding="utf-8") as out_file:
                _render_table(report, Console(file=out_file))
        else:
            _render_table(report, Console())


if __name__ == "__main__":
    main()
