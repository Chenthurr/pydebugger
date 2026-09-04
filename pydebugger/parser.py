"""Traceback parsing utilities for pydebugger."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedTraceback:
    """Structured representation of a Python traceback."""

    exception_type: str
    exception_message: str
    file_path: Optional[str]
    line_number: Optional[int]
    traceback_text: str


# Regex to match the final exception line, including qualified names, e.g.:
#   ValueError: invalid literal for int()
#   __main__.MyCustomError: something went wrong
_EXCEPTION_LINE_RE = re.compile(
    r"^(?P<type>[A-Za-z_][A-Za-z0-9_.]*):\s*(?P<message>.*)$"
)

# Regex to match File "...", line N
_FILE_LINE_RE = re.compile(
    r'^\s*File "(?P<file>[^"]+)", line (?P<line>\d+)(?:, in (?P<func>[^"]+))?'
)


def parse_traceback(stderr: str) -> Optional[ParsedTraceback]:
    """Parse a Python traceback from stderr output.

    Args:
        stderr: The stderr text captured from a subprocess run.

    Returns:
        ParsedTraceback if a traceback was found, otherwise None.
    """
    if not stderr or "Traceback" not in stderr:
        return None

    lines = stderr.splitlines()
    if not lines:
        return None

    # Find the last exception line (the one with the colon)
    exception_type = "Unknown"
    exception_message = ""
    exc_line_idx = -1

    for idx, line in enumerate(lines):
        match = _EXCEPTION_LINE_RE.match(line)
        if match:
            exception_type = match.group("type")
            exception_message = match.group("message").strip()
            exc_line_idx = idx

    # Find the most recent file/line in the traceback before the exception
    file_path: Optional[str] = None
    line_number: Optional[int] = None

    for line in lines[:exc_line_idx]:
        match = _FILE_LINE_RE.match(line)
        if match:
            file_path = match.group("file")
            line_number = int(match.group("line"))

    return ParsedTraceback(
        exception_type=exception_type,
        exception_message=exception_message,
        file_path=file_path,
        line_number=line_number,
        traceback_text=stderr.strip(),
    )
