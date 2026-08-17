"""Tests for pydebugger.storage."""

import tempfile
from pathlib import Path

import pytest

from pydebugger.storage import Storage


@pytest.fixture
def temp_storage():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        yield Storage(db_path)


def test_insert_and_get_summary(temp_storage):
    storage = temp_storage
    storage.insert_run(
        script_name="test.py",
        exit_code=1,
        exception_type="ValueError",
        category="TypeError/ValueError",
        message="bad value",
        traceback="traceback here",
        error_signature="abc123",
        duration_ms=42.0,
    )
    summary = storage.get_summary()
    assert summary["total_runs"] == 1
    assert summary["total_errors"] == 1
    assert len(summary["categories"]) == 1
    assert summary["categories"][0]["category"] == "TypeError/ValueError"


def test_get_history(temp_storage):
    storage = temp_storage
    for i in range(3):
        storage.insert_run(
            script_name="script_a.py",
            exit_code=0,
            exception_type=None,
            category=None,
            message=None,
            traceback=None,
            error_signature=None,
            duration_ms=10.0,
        )
    storage.insert_run(
        script_name="script_b.py",
        exit_code=1,
        exception_type="KeyError",
        category="KeyError/IndexError",
        message="missing key",
        traceback="tb",
        error_signature="sig1",
        duration_ms=20.0,
    )
    history = storage.get_history("script_a.py")
    assert len(history) == 3
    assert all(r.script_name == "script_a.py" for r in history)


def test_get_recent(temp_storage):
    storage = temp_storage
    for i in range(5):
        storage.insert_run(
            script_name=f"script_{i}.py",
            exit_code=1,
            exception_type="TypeError",
            category="TypeError/ValueError",
            message="err",
            traceback="tb",
            error_signature="sig",
            duration_ms=1.0,
        )
    recent = storage.get_recent(limit=3)
    assert len(recent) == 3


def test_export_jsonl(temp_storage):
    storage = temp_storage
    storage.insert_run(
        script_name="test.py",
        exit_code=1,
        exception_type="ValueError",
        category="TypeError/ValueError",
        message="bad",
        traceback="tb",
        error_signature="sig",
        duration_ms=5.0,
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "out.jsonl"
        count = storage.export_jsonl(output)
        assert count == 1
        assert output.exists()
        content = output.read_text()
        assert "test.py" in content
        assert "ValueError" in content
