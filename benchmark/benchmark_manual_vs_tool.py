#!/usr/bin/env python3
"""
Benchmark: Manual Debugging vs. pydebugger

This script compares an explicitly configured manual-diagnosis estimate against
pydebugger-assisted diagnosis for the sample scripts. It is an experiment, not
a claim about average developer productivity.

Usage:
    python benchmark/benchmark_manual_vs_tool.py
    python benchmark/benchmark_manual_vs_tool.py --manual-seconds 120 --report-seconds 15
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path


def run_pydebugger_on_samples(timeout: float) -> tuple[int, float]:
    """Run pydebugger on all sample scripts and return error count + duration."""
    sample_dir = Path(__file__).parent.parent / "sample_scripts"
    cmd = [
        sys.executable,
        "-m",
        "pydebugger.cli",
        "run",
        "--all",
        str(sample_dir),
        "--timeout",
        str(timeout),
    ]

    start = time.perf_counter()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.perf_counter() - start

    if result.returncode != 0:
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)

    error_count = result.stdout.count("✗")
    return error_count, duration


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manual-seconds",
        type=float,
        default=120.0,
        help="Assumed manual diagnosis time per error (default: 120).",
    )
    parser.add_argument(
        "--report-seconds",
        type=float,
        default=15.0,
        help="Assumed time to read the structured report (default: 15).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="Maximum runtime per sample script (default: 60).",
    )
    args = parser.parse_args()

    if args.manual_seconds <= 0 or args.report_seconds < 0 or args.timeout <= 0:
        parser.error("manual-seconds and timeout must be > 0; report-seconds must be >= 0")

    print("=" * 60)
    print("Benchmark: Manual Debugging vs. pydebugger")
    print("=" * 60)

    error_count, tool_runtime = run_pydebugger_on_samples(args.timeout)

    if error_count == 0:
        print("No errors found. Make sure sample_scripts contain buggy scripts.")
        sys.exit(1)

    manual_total_time = error_count * args.manual_seconds
    tool_total_time = tool_runtime + args.report_seconds
    time_saved = manual_total_time - tool_total_time
    reduction_pct = (time_saved / manual_total_time) * 100

    print(f"\nSample scripts with errors: {error_count}")
    print(f"Assumed manual time/error:  {args.manual_seconds:.1f}s")
    print(f"pydebugger runtime:         {tool_runtime:.2f}s")
    print(f"Estimated manual time:      {manual_total_time:.0f}s ({manual_total_time/60:.1f} min)")
    print(f"Assumed report read time:   {args.report_seconds:.1f}s")
    print(f"Estimated tool time:        {tool_total_time:.2f}s")
    print(f"Time saved:                 {time_saved:.0f}s ({time_saved/60:.1f} min)")
    print(f"Reduction in time-to-diagnosis: {reduction_pct:.1f}%")
    print("\n" + "=" * 60)
    print("NOTE: Manual and report-read times are user-supplied assumptions.")
    print("For a reproducible study, measure these times with real debugging sessions.")
    print("=" * 60)


if __name__ == "__main__":
    main()
