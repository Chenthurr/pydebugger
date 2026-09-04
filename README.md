# pydebugger

> A CLI-based Python debugging utility that runs scripts, automatically catches runtime errors, classifies them into meaningful categories, and logs them in a structured, queryable format.

## Motivation

When working with multiple Python scripts — especially in data pipelines, batch jobs, or legacy codebases — tracking down failures manually is tedious and error-prone. Developers spend significant time:

1. Re-running scripts to reproduce errors
2. Reading raw tracebacks to identify the root file and line
3. Classifying errors (Is this an import issue? A logic bug? A missing file?)
4. Documenting findings in spreadsheets or issue trackers

**pydebugger** automates this workflow. It runs your scripts as subprocesses, parses tracebacks into structured data, classifies errors by category, generates stable signatures for duplicates, and stores everything in a local SQLite database.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   CLI       │────▶│   Runner    │────▶│   Parser    │────▶│  Classifier │────▶│   Storage   │
│  (typer)    │     │ (subprocess)│     │   (regex)   │     │  (heuristics)│     │  (SQLite)  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                                       │
                                                                                       ▼
                                                                                ┌─────────────┐
                                                                                │   Report    │
                                                                                │   (rich)    │
                                                                                └─────────────┘
```

**Flow:**
1. **Runner** executes the target script via `subprocess`, capturing stdout, stderr, exit code, and duration. Each run has a configurable timeout.
2. **Parser** scans stderr for Python tracebacks and extracts exception type, message, file path, and line number, including qualified custom exception names.
3. **Classifier** maps the exception type to a high-level category. If the type is unknown, keyword heuristics on the message provide a fallback. A stable MD5-based signature is generated to detect duplicates.
4. **Storage** persists every run to a local SQLite database with indexes on script name, error signature, and timestamp.
5. **Report** uses `rich` to render summary tables, live tail views, and per-script history.

## Installation

```bash
git clone https://github.com/Chenthurr/pydebugger.git
cd pydebugger
pip install -e .
```

Or install in a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Usage

### Run a Single Script

```bash
debugtool run sample_scripts/bug_type_error.py
```

By default, each script is allowed to run for up to 60 seconds. Override the limit with `--timeout`:

```bash
debugtool run --timeout 10 sample_scripts/my_script.py
```

A timed-out run is recorded as `TimeoutError` instead of blocking indefinitely.

### Run All Scripts in a Directory

```bash
debugtool run --all sample_scripts/
```

To include nested directories:

```bash
debugtool run --all --recursive sample_scripts/
```

### View Report

```bash
debugtool report
```

### Live Tail

```bash
# Static view
debugtool tail

# Live-following mode (refreshes every 2 seconds)
debugtool tail --live
```

Press `Ctrl+C` to exit live mode.

### Script History

```bash
debugtool history bug_type_error.py
```

### Export to JSON Lines

```bash
debugtool export runs.jsonl
```

## Error Classification Logic

pydebugger uses a two-tier classification system:

### Tier 1: Exception Type Mapping

Common mappings include:

| Exception Type | Category |
|---|---|
| `ImportError`, `ModuleNotFoundError` | `ImportError` |
| `TypeError`, `ValueError` | `TypeError/ValueError` |
| `FileNotFoundError`, `IOError`, `OSError` | `IOError/FileNotFoundError` |
| `KeyError`, `IndexError` | `KeyError/IndexError` |
| `ZeroDivisionError`, `RecursionError`, `AssertionError`, `AttributeError`, `NameError` | `LogicError` |
| `MemoryError`, `TimeoutError` | `ResourceError` |

### Tier 2: Keyword Heuristics

If the exception type is unknown, the message is scanned for keywords such as `no module named`, `cannot import`, `file not found`, `permission denied`, `division by zero`, `maximum recursion`, and `missing ... required`.

### Error Signature

To detect recurring errors across runs, pydebugger generates a stable signature:

```
signature = md5(exception_type + ":" + normalized_message)[:16]
```

Normalization strips variable content such as quoted strings, memory addresses, numbers, and file paths so that semantically similar errors can share a signature. The hash is used only as a deduplication identifier, not for security.

## Benchmark: Efficiency Experiment

The repository includes a benchmark script that compares an **explicitly configured manual-diagnosis estimate** against pydebugger-assisted diagnosis. It is an experiment, not a measured claim about average developer productivity.

### Running the Benchmark

```bash
python benchmark/benchmark_manual_vs_tool.py
```

You can change the assumptions explicitly:

```bash
python benchmark/benchmark_manual_vs_tool.py --manual-seconds 120 --report-seconds 15
```

The benchmark reports the sample error count, actual pydebugger runtime, configured assumptions, estimated time saved, and calculated percentage reduction. For a real study, replace the assumptions with measured times from representative debugging sessions.

## Security Considerations

**pydebugger executes target Python scripts with the same operating-system privileges as the user running the command.** It is a debugging runner, not a sandbox. Do not use it to execute untrusted or malicious Python code unless you provide an external sandbox or other isolation boundary.

## Development

### Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=pydebugger --cov-report=term-missing
```

### Linting and Type Checking

```bash
ruff check pydebugger/ tests/ benchmark/
mypy pydebugger/
```

CI runs tests, linting, and type checking across Python 3.9–3.13.

## Contributing

Contributions are welcome! Please open an issue or pull request on GitHub.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
