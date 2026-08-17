# pydebugger

> A CLI-based Python debugging utility that runs scripts, automatically catches runtime errors, classifies them into meaningful categories, and logs them in a structured, queryable format.

## Motivation

When working with multiple Python scripts — especially in data pipelines, batch jobs, or legacy codebases — tracking down failures manually is tedious and error-prone. Developers spend significant time:

1. Re-running scripts to reproduce errors
2. Reading raw tracebacks to identify the root file and line
3. Classifying errors (Is this an import issue? A logic bug? A missing file?)
4. Documenting findings in spreadsheets or issue trackers

**pydebugger** automates this entire workflow. It runs your scripts as subprocesses, parses tracebacks into structured data, classifies errors by category, generates stable signatures for duplicates, and stores everything in a local SQLite database. The result: faster time-to-diagnosis and a searchable history of every failure.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   CLI       │────▶│   Runner    │────▶│   Parser    │────▶│  Classifier │────▶│   Storage   │
│  (typer)    │     │ (subprocess)│     │   (regex)   │     │  (heuristics)│     │  (SQLite)   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                                       │
                                                                                       ▼
                                                                                ┌─────────────┐
                                                                                │   Report    │
                                                                                │   (rich)    │
                                                                                └─────────────┘
```

**Flow:**
1. **Runner** executes the target script via `subprocess`, capturing stdout, stderr, exit code, and duration.
2. **Parser** scans stderr for Python tracebacks and extracts exception type, message, file path, and line number.
3. **Classifier** maps the exception type to a high-level category (e.g., `ImportError`, `LogicError`). If the type is unknown, keyword heuristics on the message provide a fallback. A stable MD5-based signature is generated to detect duplicates.
4. **Storage** persists every run to a local SQLite database with indexes on script name, error signature, and timestamp for fast queries.
5. **Report** uses `rich` to render summary tables, live tail views, and per-script history.

## Installation

```bash
git clone https://github.com/yourusername/pydebugger.git
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

**Sample output:**

```
Running sample_scripts/bug_type_error.py ...
✗ bug_type_error.py — TypeError (8.4 ms)
```

### Run All Scripts in a Directory

```bash
debugtool run --all sample_scripts/
```

**Sample output:**

```
Running 11 script(s) from sample_scripts/...

Running sample_scripts/bug_attribute_error.py ...
✗ bug_attribute_error.py — AttributeError (9.1 ms)
Running sample_scripts/bug_custom_logic.py ...
✗ bug_custom_logic.py — AssertionError (7.8 ms)
Running sample_scripts/bug_file_not_found.py ...
✗ bug_file_not_found.py — FileNotFoundError (8.2 ms)
Running sample_scripts/bug_import_error.py ...
✗ bug_import_error.py — ModuleNotFoundError (12.5 ms)
Running sample_scripts/bug_index_error.py ...
✗ bug_index_error.py — IndexError (7.9 ms)
Running sample_scripts/bug_key_error.py ...
✗ bug_key_error.py — KeyError (8.0 ms)
Running sample_scripts/bug_name_error.py ...
✗ bug_name_error.py — NameError (8.3 ms)
Running sample_scripts/bug_recursion_error.py ...
✗ bug_recursion_error.py — RecursionError (15.2 ms)
Running sample_scripts/bug_type_error.py ...
✗ bug_type_error.py — TypeError (8.4 ms)
Running sample_scripts/bug_value_error.py ...
✗ bug_value_error.py — ValueError (8.1 ms)
Running sample_scripts/bug_zero_division.py ...
✗ bug_zero_division.py — ZeroDivisionError (7.7 ms)
```

### View Report

```bash
debugtool report
```

**Sample output:**

```
                    pydebugger Report
    Total Runs: 11 | Total Errors: 11

┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Category               ┃ Count ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ LogicError             │ 5     │
│ TypeError/ValueError   │ 2     │
│ IOError/FileNotFound…  │ 1     │
│ ImportError            │ 1     │
│ KeyError/IndexError    │ 2     │
└────────────────────────┴───────┘

         Top 10 Most Frequent Error Signatures
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Signature        ┃ Type         ┃ Message                    ┃ Count ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ a1b2c3d4e5f6...  │ TypeError    │ unsupported operand type…  │ 1     │
│ ...              │ ...          │ ...                        │ ...   │
└──────────────────┴──────────────┴────────────────────────────┴───────┘
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

**Sample output:**

```
         Execution History: bug_type_error.py

┏━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Timestamp         ┃ Exit ┃ Category           ┃ Type      ┃ Message                  ┃ Duration (ms)┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 2026-08-17T08:... │ 1    │ TypeError/ValueEr… │ TypeError │ unsupported operand ty…  │ 8.4         │
└───────────────────┴──────┴────────────────────┴───────────┴──────────────────────────┴─────────────┘
```

### Export to JSON Lines

```bash
debugtool export runs.jsonl
```

## Error Classification Logic

pydebugger uses a two-tier classification system:

### Tier 1: Exception Type Mapping

The exception class name is the primary signal. Common mappings:

| Exception Type            | Category                |
|---------------------------|-------------------------|
| `ImportError`             | `ImportError`           |
| `ModuleNotFoundError`     | `ImportError`           |
| `TypeError`               | `TypeError/ValueError`  |
| `ValueError`              | `TypeError/ValueError`  |
| `FileNotFoundError`       | `IOError/FileNotFoundError` |
| `IOError` / `OSError`     | `IOError/FileNotFoundError` |
| `KeyError`                | `KeyError/IndexError`   |
| `IndexError`              | `KeyError/IndexError`   |
| `ZeroDivisionError`       | `LogicError`            |
| `RecursionError`          | `LogicError`            |
| `AssertionError`          | `LogicError`            |
| `AttributeError`          | `LogicError`            |
| `NameError`               | `LogicError`            |
| `MemoryError`             | `ResourceError`         |
| `TimeoutError`            | `ResourceError`         |

### Tier 2: Keyword Heuristics

If the exception type is unknown (e.g., a custom exception), the message is scanned for keywords:

| Keyword Pattern                  | Fallback Category       |
|----------------------------------|-------------------------|
| `no module named`                | `ImportError`           |
| `cannot import`                  | `ImportError`           |
| `file not found` / `no such file`| `IOError/FileNotFoundError` |
| `permission denied`              | `IOError/FileNotFoundError` |
| `division by zero`               | `LogicError`            |
| `maximum recursion`              | `LogicError`            |
| `not supported between instances`| `TypeError/ValueError`  |
| `missing ... required`           | `TypeError/ValueError`  |

### Error Signature

To detect recurring errors across runs, pydebugger generates a stable signature:

```
signature = md5(exception_type + ":" + normalized_message)[:16]
```

Normalization strips variable content (quoted strings, memory addresses, numbers, file paths) so that semantically identical errors produce the same signature even if their messages differ slightly.

## Benchmark: Efficiency Metric

The repository includes a benchmark script that compares **manual debugging time** against **pydebugger-assisted diagnosis**.

### Methodology

1. **Manual debugging time** is estimated at ~2 minutes per error (reading traceback, identifying root cause, documenting).
2. **Tool time** is the sum of pydebugger runtime plus ~15 seconds to read the structured report.
3. The benchmark runs all 11 sample scripts and computes the percentage reduction.

### Running the Benchmark

```bash
python benchmark/benchmark_manual_vs_tool.py
```

### Expected Output

```
============================================================
Benchmark: Manual Debugging vs. pydebugger
============================================================

Sample scripts with errors: 11
pydebugger runtime:          0.15s
Estimated manual time:       1320s (22.0 min)
Estimated tool time:         15.15s
Time saved:                  1305s (21.8 min)
Reduction in time-to-diagnosis: [X]%
```

> **Note:** The `[X]%` placeholder should be replaced with the actual measured value after running the benchmark. Based on the estimates above, the expected reduction is approximately **98.9%**.

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
ruff check pydebugger/
mypy pydebugger/
```

## Contributing

Contributions are welcome! Please open an issue or pull request on GitHub.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
