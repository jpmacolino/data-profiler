from __future__ import annotations

import json
import subprocess
import sys

import pytest

FIXTURE_CSV = "tests/fixtures/sample.csv"
FIXTURE_JSONL = "tests/fixtures/sample.jsonl"
CWD = "c:/dev/data-profiler"

_PROFILE_REPORT_KEYS = {"row_count", "column_count", "columns", "quality_issues"}


def _run(*args: str) -> subprocess.CompletedProcess:
    """Run the CLI via `python -m data_profiler.cli` and return the result."""
    return subprocess.run(
        [sys.executable, "-m", "data_profiler.cli", *args],
        capture_output=True,
        text=True,
        cwd=CWD,
    )


# ===========================================================================
# Smoke tests — CSV fixture
# ===========================================================================

def test_csv_fixture_exits_zero():
    result = _run(FIXTURE_CSV)
    assert result.returncode == 0


def test_json_format_exits_zero():
    result = _run(FIXTURE_CSV, "--format", "json")
    assert result.returncode == 0


def test_json_format_stdout_is_parseable():
    result = _run(FIXTURE_CSV, "--format", "json")
    parsed = json.loads(result.stdout)
    assert isinstance(parsed, dict)


def test_json_format_output_has_profile_report_shape():
    result = _run(FIXTURE_CSV, "--format", "json")
    parsed = json.loads(result.stdout)
    assert _PROFILE_REPORT_KEYS <= parsed.keys()


# ===========================================================================
# --output flag
# ===========================================================================

def test_output_flag_creates_file(tmp_path):
    out = tmp_path / "report.txt"
    result = _run(FIXTURE_CSV, "--output", str(out))
    assert result.returncode == 0
    assert out.exists()


def test_output_flag_file_is_non_empty(tmp_path):
    out = tmp_path / "report.txt"
    _run(FIXTURE_CSV, "--output", str(out))
    assert out.stat().st_size > 0


def test_output_flag_json_writes_valid_json(tmp_path):
    out = tmp_path / "report.json"
    result = _run(FIXTURE_CSV, "--format", "json", "--output", str(out))
    assert result.returncode == 0
    parsed = json.loads(out.read_text(encoding="utf-8"))
    assert _PROFILE_REPORT_KEYS <= parsed.keys()


# ===========================================================================
# Error cases
# ===========================================================================

def test_nonexistent_file_exits_nonzero():
    result = _run("tests/fixtures/does_not_exist.csv")
    assert result.returncode != 0


def test_unknown_extension_exits_nonzero(tmp_path):
    # Write a valid CSV body to a file with an unrecognized extension.
    bad_ext = tmp_path / "data.dat"
    bad_ext.write_text("name,age\nAlice,30\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "data_profiler.cli", str(bad_ext)],
        capture_output=True,
        text=True,
        cwd=CWD,
    )
    assert result.returncode != 0


def test_unknown_extension_error_message_mentions_input_format(tmp_path):
    bad_ext = tmp_path / "data.dat"
    bad_ext.write_text("name,age\nAlice,30\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "data_profiler.cli", str(bad_ext)],
        capture_output=True,
        text=True,
        cwd=CWD,
    )
    assert "--input-format" in result.stderr


# ===========================================================================
# --input-format flag
# ===========================================================================

def test_input_format_csv_on_csv_fixture_exits_zero():
    result = _run(FIXTURE_CSV, "--input-format", "csv")
    assert result.returncode == 0


def test_input_format_jsonl_on_jsonl_fixture_exits_zero():
    result = _run(FIXTURE_JSONL, "--input-format", "jsonl")
    assert result.returncode == 0


def test_input_format_jsonl_auto_detected_exits_zero():
    result = _run(FIXTURE_JSONL)
    assert result.returncode == 0


def test_input_format_csv_produces_correct_row_count():
    result = _run(FIXTURE_CSV, "--format", "json")
    parsed = json.loads(result.stdout)
    assert parsed["row_count"] == 5


def test_input_format_jsonl_produces_correct_row_count():
    result = _run(FIXTURE_JSONL, "--format", "json")
    parsed = json.loads(result.stdout)
    assert parsed["row_count"] == 3
