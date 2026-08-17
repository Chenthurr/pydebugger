"""CLI entry point for pydebugger using Typer."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from pydebugger.classifier import classify_error
from pydebugger.parser import parse_traceback
from pydebugger.report import live_tail, print_history, print_summary, print_tail
from pydebugger.runner import discover_scripts, run_script
from pydebugger.storage import Storage

app = typer.Typer(
    name="pydebugger",
    help="A CLI-based Python debugging utility.",
    no_args_is_help=True,
)
console = Console()


def _process_run(script_path: str, storage: Storage) -> None:
    """Run a single script, parse errors, classify, and log to storage."""
    console.print(f"[dim]Running {script_path} ...[/dim]")
    result = run_script(script_path)

    exception_type: Optional[str] = None
    exception_message: Optional[str] = None
    category: Optional[str] = None
    signature: Optional[str] = None
    traceback_text: Optional[str] = None

    if result.exit_code != 0 and result.stderr:
        parsed = parse_traceback(result.stderr)
        if parsed:
            exception_type = parsed.exception_type
            exception_message = parsed.exception_message
            traceback_text = parsed.traceback_text
            classification = classify_error(exception_type, exception_message)
            category = classification.category
            signature = classification.error_signature
        else:
            # Non-traceback stderr output
            exception_type = "NonZeroExit"
            exception_message = result.stderr.strip()[:200]
            category = "Unknown"
            signature = classify_error(exception_type, exception_message).error_signature
            traceback_text = result.stderr.strip()

    storage.insert_run(
        script_name=Path(script_path).name,
        exit_code=result.exit_code,
        exception_type=exception_type,
        category=category,
        message=exception_message,
        traceback=traceback_text,
        error_signature=signature,
        duration_ms=result.duration_ms,
    )

    if result.exit_code == 0:
        console.print(
            f"[green]✓[/green] {Path(script_path).name} "
            f"({result.duration_ms:.1f} ms)"
        )
    else:
        console.print(
            f"[red]✗[/red] {Path(script_path).name} — "
            f"{exception_type or 'Error'} "
            f"({result.duration_ms:.1f} ms)"
        )


@app.command()
def run(
    target: str = typer.Argument(..., help="Python script or directory to run."),
    all_scripts: bool = typer.Option(
        False, "--all", "-a", help="Run all .py files in the target directory."
    ),
    db_path: Optional[str] = typer.Option(
        None, "--db", help="Path to SQLite database (default: ~/.pydebugger/runs.db)."
    ),
) -> None:
    """Run a Python script (or all scripts in a directory) and log results."""
    storage = Storage(Path(db_path) if db_path else None)

    if all_scripts:
        scripts = discover_scripts(target)
        if not scripts:
            console.print(f"[yellow]No .py files found in {target}[/yellow]")
            raise typer.Exit(1)

        console.print(f"[bold]Running {len(scripts)} script(s) from {target}...[/bold]\n")
        for script in scripts:
            _process_run(script, storage)
    else:
        if not Path(target).is_file():
            console.print(f"[red]File not found: {target}[/red]")
            raise typer.Exit(1)
        _process_run(target, storage)


@app.command()
def report(
    db_path: Optional[str] = typer.Option(
        None, "--db", help="Path to SQLite database."
    ),
) -> None:
    """Show a summary report of all recorded runs."""
    storage = Storage(Path(db_path) if db_path else None)
    print_summary(storage)


@app.command()
def tail(
    live: bool = typer.Option(
        False, "--live", "-l", help="Live-follow mode (refresh every 2s)."
    ),
    limit: int = typer.Option(20, "--limit", "-n", help="Number of recent records to show."),
    db_path: Optional[str] = typer.Option(
        None, "--db", help="Path to SQLite database."
    ),
) -> None:
    """Show the most recent errors. Use --live for real-time updates."""
    storage = Storage(Path(db_path) if db_path else None)

    if live:
        live_tail(storage)
    else:
        records = storage.get_recent(limit=limit)
        print_tail(records)


@app.command()
def history(
    script: str = typer.Argument(..., help="Script name to look up history for."),
    limit: int = typer.Option(50, "--limit", "-n", help="Max records to show."),
    db_path: Optional[str] = typer.Option(
        None, "--db", help="Path to SQLite database."
    ),
) -> None:
    """Show past runs and errors for a specific script."""
    storage = Storage(Path(db_path) if db_path else None)
    records = storage.get_history(script, limit=limit)
    print_history(records, script)


@app.command()
def export(
    output: str = typer.Argument(..., help="Output JSONL file path."),
    db_path: Optional[str] = typer.Option(
        None, "--db", help="Path to SQLite database."
    ),
) -> None:
    """Export all records to JSON Lines format."""
    storage = Storage(Path(db_path) if db_path else None)
    count = storage.export_jsonl(Path(output))
    console.print(f"[green]Exported {count} record(s) to {output}[/green]")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
