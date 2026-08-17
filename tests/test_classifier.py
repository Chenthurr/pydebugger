"""Tests for pydebugger.classifier."""

import pytest

from pydebugger.classifier import classify_error, generate_signature


def test_classify_import_error():
    result = classify_error("ImportError", "No module named 'numpy'")
    assert result.category == "ImportError"
    assert result.exception_type == "ImportError"


def test_classify_module_not_found():
    result = classify_error("ModuleNotFoundError", "No module named 'fake'")
    assert result.category == "ImportError"


def test_classify_type_error():
    result = classify_error("TypeError", "unsupported operand type(s)")
    assert result.category == "TypeError/ValueError"


def test_classify_value_error():
    result = classify_error("ValueError", "invalid literal for int()")
    assert result.category == "TypeError/ValueError"


def test_classify_file_not_found():
    result = classify_error("FileNotFoundError", "No such file or directory")
    assert result.category == "IOError/FileNotFoundError"


def test_classify_zero_division():
    result = classify_error("ZeroDivisionError", "division by zero")
    assert result.category == "LogicError"


def test_classify_key_error():
    result = classify_error("KeyError", "'missing_key'")
    assert result.category == "KeyError/IndexError"


def test_classify_index_error():
    result = classify_error("IndexError", "list index out of range")
    assert result.category == "KeyError/IndexError"


def test_classify_unknown_with_heuristic():
    result = classify_error("SomeCustomError", "No module named 'something'")
    assert result.category == "ImportError"


def test_classify_fully_unknown():
    result = classify_error("WeirdError", "something completely unexpected")
    assert result.category == "Unknown"


def test_signature_stability():
    sig1 = generate_signature("ValueError", "invalid literal for int() with base 10: 'abc'")
    sig2 = generate_signature("ValueError", "invalid literal for int() with base 10: 'xyz'")
    assert sig1 == sig2  # Normalization should make them equal


def test_signature_different_types():
    sig1 = generate_signature("ValueError", "bad value")
    sig2 = generate_signature("TypeError", "bad value")
    assert sig1 != sig2
