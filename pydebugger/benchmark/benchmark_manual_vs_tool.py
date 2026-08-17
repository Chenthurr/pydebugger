#!/usr/bin/env python3
"""
Benchmark: Manual Debugging vs. pydebugger

This script simulates the time cost of manually debugging a set of buggy
scripts versus using pydebugger to automatically classify and log errors.

Methodology:
1. Run all sample scripts through pydebugger.
2. For each error, estimate the "manual debugging time" (time a developer
   would spend reading traceback, identifying the file/line, classifying
   the error, and documenting it).
3. Compare against the "tool time" (time to run pydebugger + time to
   read the structured report).
4. Compute percentage reduction in time-to-diagnosis.

Usage:
    python benchmark/benchmark_manual_vs_tool.py
"""

import subprocess
import sys
import time
from pathlib import Path

# Estimated average time (in seconds) for a developer to manually diagnose
# and document one error from a raw traceback.
MANUAL_TIME_PER_ERROR = 120  # 2 minutes

# Estimated time (in seconds) to read the pydebugger report for all errors.
TOOL_REPORT_READ_TIME = 15  # 15 seconds


def run_pydebugger_on_samples() -> tuple[int, float]:
    """Run pydebugger on all sample scripts and return error count + duration."""
    sample_dir = Path(__file__).parent.parent / "sample_scripts"
    cmd = [sys.executable, "-m", "pydebugger.cli", "run", "--all", str(sample_dir)]

    start = time.perf_counter()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.perf_counter() - start

    # Count errors from stderr (each error line starts with ✗)
    error_count = result.stdout.count("✗")
    return error_count, duration


def main() -> None:
    print("=" * 60)
    print("Benchmark: Manual Debugging vs. pydebugger")
    print("=" * 60)

    error_count, tool_runtime = run_pydebugger_on_samples()

    if error_count == 0:
        print("No errors found. Make sure sample_scripts contain buggy scripts.")
        sys.exit(1)

    manual_total_time = error_count * MANUAL_TIME_PER_ERROR
    tool_total_time = tool_runtime + TOOL_REPORT_READ_TIME
    time_saved = manual_total_time - tool_total_time
    reduction_pct = (time_saved / manual_total_time) * 100

    print(f"\nSample scripts with errors: {error_count}")
    print(f"pydebugger runtime:          {tool_runtime:.2f}s")
    print(f"Estimated manual time:       {manual_total_time:.0f}s ({manual_total_time/60:.1f} min)")
    print(f"Estimated tool time:         {tool_total_time:.2f}s")
    print(f"Time saved:                  {time_saved:.0f}s ({time_saved/60:.1f} min)")
    print(f"Reduction in time-to-diagnosis: [bold green]{reduction_pct:.1f}%[/bold green]")
    print("\n" + "=" * 60)
    print(
        "NOTE: Manual time is an estimate based on average developer\n"
        "productivity studies. Actual results will vary by team and codebase."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
