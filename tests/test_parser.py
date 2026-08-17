"""Tests for pydebugger.parser."""

import pytest

from pydebugger.parser import parse_traceback


SIMPLE_TRACEBACK = """Traceback (most recent call last):
  File "/home/user/project/script.py", line 10, in <module>
    main()
  File "/home/user/project/script.py", line 5, in main
    result = 1 / 0
ZeroDivisionError: division by zero
"""

MULTI_LINE_MESSAGE = """Traceback (most recent call last):
  File "/app/run.py", line 20, in <module>
    load_config()
  File "/app/config.py", line 8, in load_config
    raise ValueError("Invalid configuration file: missing required key 'database_url'")
ValueError: Invalid configuration file: missing required key 'database_url'
"""

NO_TRACEBACK = "Just some stderr output without a traceback\n"

EMPTY = ""

CUSTOM_EXCEPTION = """Traceback (most recent call last):
  File "/app/main.py", line 3, in <module>
    raise MyCustomError("something went wrong")
__main__.MyCustomError: something went wrong
"""


def test_parse_simple_traceback():
    result = parse_traceback(SIMPLE_TRACEBACK)
    assert result is not None
    assert result.exception_type == "ZeroDivisionError"
    assert result.exception_message == "division by zero"
    assert result.file_path == "/home/user/project/script.py"
    assert result.line_number == 5
    assert "Traceback" in result.traceback_text


def test_parse_multi_line_message():
    result = parse_traceback(MULTI_LINE_MESSAGE)
    assert result is not None
    assert result.exception_type == "ValueError"
    assert "missing required key" in result.exception_message
    assert result.file_path == "/app/config.py"
    assert result.line_number == 8


def test_parse_no_traceback():
    result = parse_traceback(NO_TRACEBACK)
    assert result is None


def test_parse_empty():
    result = parse_traceback(EMPTY)
    assert result is None


def test_parse_custom_exception():
    result = parse_traceback(CUSTOM_EXCEPTION)
    assert result is not None
    assert result.exception_type == "__main__.MyCustomError"
    assert result.exception_message == "something went wrong"
    assert result.file_path == "/app/main.py"
    assert result.line_number == 3
