from pydebugger.classifier import classify_error, generate_signature


def test_unknown_exception_with_import_message_uses_heuristic():
    result = classify_error("CustomImportFailure", "No module named optional_backend")

    assert result.category == "ImportError"
    assert result.exception_type == "CustomImportFailure"


def test_signature_normalizes_variable_values():
    first = generate_signature("ValueError", "invalid value 123 in /tmp/run-a.txt")
    second = generate_signature("ValueError", "invalid value 456 in /tmp/run-b.txt")

    assert first == second


def test_known_exception_type_takes_precedence_over_message_heuristics():
    result = classify_error("TypeError", "file not found while processing input")

    assert result.category == "TypeError/ValueError"
