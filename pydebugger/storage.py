"""SQLite-backed structured logging for pydebugger."""

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional


DEFAULT_DB_PATH = Path.home() / ".pydebugger" / "runs.db"


@dataclass
class LogRecord:
    """A single logged execution record."""

    id: int
    timestamp: str
    script_name: str
    exit_code: int
    exception_type: Optional[str]
    category: Optional[str]
    message: Optional[str]
    traceback: Optional[str]
    error_signature: Optional[str]
    duration_ms: float


class Storage:
    """SQLite storage backend for pydebugger execution logs."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the SQLite schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    script_name TEXT NOT NULL,
                    exit_code INTEGER NOT NULL,
                    exception_type TEXT,
                    category TEXT,
                    message TEXT,
                    traceback TEXT,
                    error_signature TEXT,
                    duration_ms REAL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_runs_signature ON runs(error_signature)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_runs_script ON runs(script_name)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_runs_timestamp ON runs(timestamp)"
            )
            conn.commit()

    def insert_run(
        self,
        script_name: str,
        exit_code: int,
        exception_type: Optional[str],
        category: Optional[str],
        message: Optional[str],
        traceback: Optional[str],
        error_signature: Optional[str],
        duration_ms: float,
    ) -> int:
        """Insert a new run record and return its ID."""
        timestamp = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO runs
                (timestamp, script_name, exit_code, exception_type, category,
                 message, traceback, error_signature, duration_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    timestamp,
                    script_name,
                    exit_code,
                    exception_type,
                    category,
                    message,
                    traceback,
                    error_signature,
                    duration_ms,
                ),
            )
            conn.commit()
            return cursor.lastrowid or 0

    def get_summary(self) -> dict:
        """Return aggregate statistics about all recorded runs."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            total = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
            errors = conn.execute(
                "SELECT COUNT(*) FROM runs WHERE exit_code != 0"
            ).fetchone()[0]

            categories = conn.execute(
                """
                SELECT category, COUNT(*) as count
                FROM runs
                WHERE category IS NOT NULL
                GROUP BY category
                ORDER BY count DESC
                """
            ).fetchall()

            signatures = conn.execute(
                """
                SELECT error_signature, exception_type, message, COUNT(*) as count
                FROM runs
                WHERE error_signature IS NOT NULL
                GROUP BY error_signature
                ORDER BY count DESC
                LIMIT 10
                """
            ).fetchall()

        return {
            "total_runs": total,
            "total_errors": errors,
            "categories": [dict(row) for row in categories],
            "top_signatures": [dict(row) for row in signatures],
        }

    def get_history(self, script_name: str, limit: int = 50) -> List[LogRecord]:
        """Return execution history for a specific script."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT * FROM runs
                WHERE script_name = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (script_name, limit),
            ).fetchall()
        return [LogRecord(**dict(row)) for row in rows]

    def get_recent(self, limit: int = 20) -> List[LogRecord]:
        """Return the most recent runs across all scripts."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT * FROM runs
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [LogRecord(**dict(row)) for row in rows]

    def export_jsonl(self, output_path: Path) -> int:
        """Export all records to JSON Lines format."""
        count = 0
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM runs ORDER BY timestamp").fetchall()

        with open(output_path, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(dict(row), default=str) + "\n")
                count += 1
        return count
