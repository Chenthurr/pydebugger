# Usage Guide

## Installation

```bash
git clone https://github.com/yourusername/pydebugger.git
cd pydebugger
pip install -e .
```

## Running a Single Script

```bash
debugtool run sample_scripts/bug_type_error.py
```

Output:

```
Running sample_scripts/bug_type_error.py ...
✗ bug_type_error.py — TypeError (12.3 ms)
```

## Running All Scripts in a Directory

```bash
debugtool run --all sample_scripts/
```

## Viewing the Report

```bash
debugtool report
```

Shows:
- Total runs and errors
- Errors grouped by category
- Top 10 most frequent error signatures

## Live Tail

```bash
# Static view of recent errors
debugtool tail

# Live-following mode (refreshes every 2 seconds)
debugtool tail --live
```

Press `Ctrl+C` to exit live mode.

## Viewing History for a Script

```bash
debugtool history bug_type_error.py
```

## Exporting Data

```bash
debugtool export runs.jsonl
```

Exports all records to JSON Lines format for external analysis.

## Custom Database Location

All commands accept a `--db` option:

```bash
debugtool run script.py --db /path/to/custom.db
debugtool report --db /path/to/custom.db
```
