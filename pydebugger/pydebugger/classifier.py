"""Error classification and signature generation for pydebugger."""

import hashlib
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ClassificationResult:
    """Result of classifying an error."""

    category: str
    error_signature: str
    exception_type: str
    exception_message: str


# Primary mapping: exception type -> category
_TYPE_TO_CATEGORY = {
    "ImportError": "ImportError",
    "ModuleNotFoundError": "ImportError",
    "TypeError": "TypeError/ValueError",
    "ValueError": "TypeError/ValueError",
    "FileNotFoundError": "IOError/FileNotFoundError",
    "IOError": "IOError/FileNotFoundError",
    "OSError": "IOError/FileNotFoundError",
    "PermissionError": "IOError/FileNotFoundError",
    "KeyError": "KeyError/IndexError",
    "IndexError": "KeyError/IndexError",
    "ZeroDivisionError": "LogicError",
    "RecursionError": "LogicError",
    "AssertionError": "LogicError",
    "AttributeError": "LogicError",
    "NameError": "LogicError",
    "UnboundLocalError": "LogicError",
    "RuntimeError": "LogicError",
    "NotImplementedError": "LogicError",
    "StopIteration": "LogicError",
    "MemoryError": "ResourceError",
    "TimeoutError": "ResourceError",
}

# Secondary keyword heuristics for message-based classification
_KEYWORD_HEURISTICS = [
    (re.compile(r"\bno module named\b", re.IGNORECASE), "ImportError"),
    (re.compile(r"\bcannot import\b", re.IGNORECASE), "ImportError"),
    (re.compile(r"\bfile not found\b", re.IGNORECASE), "IOError/FileNotFoundError"),
    (re.compile(r"\bno such file\b", re.IGNORECASE), "IOError/FileNotFoundError"),
    (re.compile(r"\bpermission denied\b", re.IGNORECASE), "IOError/FileNotFoundError"),
    (re.compile(r"\bdivision by zero\b", re.IGNORECASE), "LogicError"),
    (re.compile(r"\bmaximum recursion\b", re.IGNORECASE), "LogicError"),
    (re.compile(r"\bassertion failed\b", re.IGNORECASE), "LogicError"),
    (re.compile(r"\bnot supported between instances\b", re.IGNORECASE), "TypeError/ValueError"),
    (re.compile(r"\bmissing\b.*\brequired\b", re.IGNORECASE), "TypeError/ValueError"),
]


def _normalize_message(message: str) -> str:
    """Normalize an exception message for signature generation.

    Removes variable parts like file paths, line numbers, memory addresses,
    and specific identifiers to produce a stable signature.
    """
    normalized = message.lower().strip()
    # Remove quoted strings (often variable content)
    normalized = re.sub(r"'[^']+'", "'<?>?'", normalized)
    normalized = re.sub(r'"[^"]+"', '"<?>?"', normalized)
    # Remove memory addresses like 0x7f8b3c2a1d00
    normalized = re.sub(r"0x[0-9a-f]+", "0x?", normalized)
    # Remove specific numbers
    normalized = re.sub(r"\b\d+\b", "?", normalized)
    # Remove file paths
    normalized = re.sub(r"[/\\][^\s]+", "<?>", normalized)
    # Collapse whitespace
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def generate_signature(exception_type: str, exception_message: str) -> str:
    """Generate a stable error signature from exception type and message.

    Args:
        exception_type: The exception class name.
        exception_message: The exception message text.

    Returns:
        A short hex hash string representing the error signature.
    """
    normalized = _normalize_message(exception_message)
    payload = f"{exception_type}:{normalized}"
    return hashlib.md5(payload.encode("utf-8")).hexdigest()[:16]


def classify_error(
    exception_type: str,
    exception_message: str,
) -> ClassificationResult:
    """Classify an error into a category and generate its signature.

    Args:
        exception_type: The exception class name.
        exception_message: The exception message text.

    Returns:
        ClassificationResult with category and signature.
    """
    category = _TYPE_TO_CATEGORY.get(exception_type, "Unknown")

    # If primary mapping gives Unknown, try keyword heuristics
    if category == "Unknown":
        for pattern, cat in _KEYWORD_HEURISTICS:
            if pattern.search(exception_message):
                category = cat
                break

    signature = generate_signature(exception_type, exception_message)

    return ClassificationResult(
        category=category,
        error_signature=signature,
        exception_type=exception_type,
        exception_message=exception_message,
    )
