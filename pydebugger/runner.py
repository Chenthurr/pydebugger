"""Subprocess execution and output capture for pydebugger."""

import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class RunResult:
    """Result of executing a Python script."""

    script_path: str
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    exception_type: Optional[str] = None
    exception_message: Optional[str] = None
    traceback_text: Optional[str] = None


def run_script(script_path: str, python_executable: Optional[str] = None) -> RunResult:
    """Run a Python script in a subprocess and capture all outputs.

    Args:
        script_path: Path to the Python script to execute.
        python_executable: Python interpreter to use (defaults to sys.executable).

    Returns:
        RunResult with captured outputs and metadata.
    """
    python = python_executable or sys.executable
    cmd = [python, str(script_path)]

    start = time.perf_counter()
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
    duration_ms = (time.perf_counter() - start) * 1000

    return RunResult(
        script_path=str(script_path),
        exit_code=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
        duration_ms=duration_ms,
    )


def discover_scripts(directory: str) -> List[str]:
    """Discover all .py files in a directory, sorted alphabetically.

    Args:
        directory: Path to the directory to scan.

    Returns:
        List of paths to Python scripts.
    """
    path = Path(directory)
    if not path.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    scripts = sorted(path.glob("*.py"))
    return [str(s) for s in scripts]
