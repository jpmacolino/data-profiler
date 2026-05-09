## Purpose 
- data-profiler is a CLI for exploratory data analysis — the 'unfamiliar dataset' moment, not production validation.

## Architecture
- `cli.py` — argparse, rich, I/O. Knows about the user.
- `profiler.py` — orchestration. Knows about the modules below but not the CLI.
- `inference.py`, `stats.py`, `quality.py` — pure functions over DataFrames. No I/O, no CLI knowledge.
- `report.py` — rendering (terminal table, JSON).
- Dependencies flow downward only — cli may import from profiler, profiler may import from inference/stats/quality, never the reverse.
- Fixtures in `tests/fixtures/`.

## Conventions
- Dependencies are intentionally minimal. Justify any addition before adding.
- Type hints on all public functions. Docstrings on all public functions.
- Commit messages follow Conventional Commits (https://www.conventionalcommits.org/)