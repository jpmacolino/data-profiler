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
- - **After subagent return:** Act directly on follow-ups with small blast radius — single-file edits, fixes scoped to what the subagent reviewed, verification runs. Surface to the user when the blast radius grows — multi-file refactors, changes to public contracts, anything that requires undoing more than one commit if wrong. Don't dispatch a follow-up subagent unless the follow-up itself warrants one.
- For shell commands, prefer bash with forward-slash paths. PowerShell invocations on this system have intermittent output-capture issues; fall back to PowerShell only if bash is unavailable or a Windows-specific command is required.