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
    timed_out: bool = False


def run_script(
    script_path: str,
    python_executable: Optional[str] = None,
    timeout: Optional[float] = None,
) -> RunResult:
    """Run a Python script in a subprocess and capture all outputs.

    Args:
        script_path: Path to the Python script to execute.
        python_executable: Python interpreter to use (defaults to sys.executable).
        timeout: Maximum execution time in seconds. ``None`` disables the timeout.

    Returns:
        RunResult with captured outputs and metadata. A timed-out process returns
        ``exit_code=124`` and ``timed_out=True`` instead of raising.
    """
    python = python_executable or sys.executable
    cmd = [python, str(script_path)]

    start = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        duration_ms = (time.perf_counter() - start) * 1000
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")
        timeout_message = f"Execution timed out after {timeout:g} seconds."
        stderr = f"{stderr.rstrip()}\n{timeout_message}".strip()
        return RunResult(
            script_path=str(script_path),
            exit_code=124,
            stdout=stdout,
            stderr=stderr,
            duration_ms=duration_ms,
            exception_type="TimeoutError",
            exception_message=timeout_message,
            timed_out=True,
        )

    duration_ms = (time.perf_counter() - start) * 1000

    return RunResult(
        script_path=str(script_path),
        exit_code=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
        duration_ms=duration_ms,
    )


def discover_scripts(directory: str, recursive: bool = False) -> List[str]:
    """Discover .py files in a directory, sorted alphabetically.

    Args:
        directory: Path to the directory to scan.
        recursive: If true, include Python files in nested directories.

    Returns:
        List of paths to Python scripts.
    """
    path = Path(directory)
    if not path.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    pattern = "**/*.py" if recursive else "*.py"
    scripts = sorted(path.glob(pattern))
    return [str(s) for s in scripts]
