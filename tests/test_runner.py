"""Tests for pydebugger.runner."""

import sys

import pytest

from pydebugger.runner import discover_scripts, run_script


def test_run_script_success(tmp_path):
    script = tmp_path / "ok.py"
    script.write_text("print('hello')\n", encoding="utf-8")

    result = run_script(str(script), python_executable=sys.executable, timeout=5)

    assert result.exit_code == 0
    assert result.stdout.strip() == "hello"
    assert result.stderr == ""
    assert result.timed_out is False
    assert result.duration_ms >= 0


def test_run_script_failure(tmp_path):
    script = tmp_path / "bad.py"
    script.write_text("raise ValueError('bad value')\n", encoding="utf-8")

    result = run_script(str(script), python_executable=sys.executable, timeout=5)

    assert result.exit_code != 0
    assert "ValueError" in result.stderr
    assert result.timed_out is False


def test_run_script_timeout(tmp_path):
    script = tmp_path / "slow.py"
    script.write_text("import time\ntime.sleep(2)\n", encoding="utf-8")

    result = run_script(str(script), python_executable=sys.executable, timeout=0.1)

    assert result.exit_code == 124
    assert result.timed_out is True
    assert result.exception_type == "TimeoutError"
    assert "timed out" in result.exception_message.lower()
    assert "timed out" in result.stderr.lower()


def test_discover_scripts_non_recursive(tmp_path):
    (tmp_path / "one.py").write_text("", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "two.py").write_text("", encoding="utf-8")

    scripts = discover_scripts(str(tmp_path))

    assert scripts == [str(tmp_path / "one.py")]


def test_discover_scripts_recursive(tmp_path):
    (tmp_path / "one.py").write_text("", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "two.py").write_text("", encoding="utf-8")

    scripts = discover_scripts(str(tmp_path), recursive=True)

    assert scripts == [str(tmp_path / "nested" / "two.py"), str(tmp_path / "one.py")]


def test_discover_scripts_requires_directory(tmp_path):
    with pytest.raises(ValueError, match="Not a directory"):
        discover_scripts(str(tmp_path / "missing"))
