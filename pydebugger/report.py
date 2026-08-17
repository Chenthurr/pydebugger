"""Rich-formatted reporting and live tail for pydebugger."""

from typing import List, Optional

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pydebugger.storage import LogRecord, Storage


console = Console()


def print_summary(storage: Storage) -> None:
    """Print a rich-formatted summary report."""
    summary = storage.get_summary()

    console.print()
    console.print(
        Panel.fit(
            f"[bold cyan]pydebugger Report[/bold cyan]\n"
            f"Total Runs: [bold]{summary['total_runs']}[/bold] | "
            f"Total Errors: [bold red]{summary['total_errors']}[/bold red]",
            title="Summary",
            border_style="cyan",
        )
    )

    if summary["categories"]:
        cat_table = Table(title="Errors by Category", show_header=True, header_style="bold magenta")
        cat_table.add_column("Category", style="cyan")
        cat_table.add_column("Count", justify="right", style="red")
        for row in summary["categories"]:
            cat_table.add_row(row["category"], str(row["count"]))
        console.print(cat_table)

    if summary["top_signatures"]:
        sig_table = Table(title="Top 10 Most Frequent Error Signatures", show_header=True, header_style="bold magenta")
        sig_table.add_column("Signature", style="dim")
        sig_table.add_column("Type", style="cyan")
        sig_table.add_column("Message", style="yellow")
        sig_table.add_column("Count", justify="right", style="red")
        for row in summary["top_signatures"]:
            msg = (row["message"] or "")[:60]
            sig_table.add_row(
                row["error_signature"][:16],
                row["exception_type"] or "N/A",
                msg,
                str(row["count"]),
            )
        console.print(sig_table)

    console.print()


def print_history(records: List[LogRecord], script_name: str) -> None:
    """Print execution history for a specific script."""
    if not records:
        console.print(f"[yellow]No history found for {script_name}[/yellow]")
        return

    console.print()
    console.print(
        Panel.fit(
            f"[bold cyan]Execution History: {script_name}[/bold cyan]",
            border_style="cyan",
        )
    )

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Timestamp", style="dim")
    table.add_column("Exit", justify="right")
    table.add_column("Category", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("Message")
    table.add_column("Duration (ms)", justify="right", style="green")

    for rec in records:
        exit_style = "green" if rec.exit_code == 0 else "red"
        msg = (rec.message or "")[:50]
        table.add_row(
            rec.timestamp[:19],
            f"[{exit_style}]{rec.exit_code}[/{exit_style}]",
            rec.category or "—",
            rec.exception_type or "—",
            msg,
            f"{rec.duration_ms:.1f}",
        )

    console.print(table)
    console.print()


def print_tail(records: List[LogRecord]) -> None:
    """Print the most recent error records."""
    if not records:
        console.print("[yellow]No records found.[/yellow]")
        return

    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]Recent Errors[/bold cyan]",
            border_style="cyan",
        )
    )

    for rec in records:
        if rec.exit_code == 0:
            continue
        title = f"[bold red]{rec.script_name}[/bold red] — {rec.timestamp[:19]}"
        content = Text()
        content.append(f"Type: ", style="bold")
        content.append(f"{rec.exception_type}\n", style="yellow")
        content.append(f"Category: ", style="bold")
        content.append(f"{rec.category}\n", style="cyan")
        content.append(f"Message: ", style="bold")
        content.append(f"{rec.message}\n", style="white")
        content.append(f"Signature: ", style="bold")
        content.append(f"{rec.error_signature}\n", style="dim")
        content.append(f"Duration: ", style="bold")
        content.append(f"{rec.duration_ms:.1f} ms", style="green")
        console.print(Panel(content, title=title, border_style="red"))

    console.print()


def live_tail(storage: Storage, refresh_interval: float = 2.0) -> None:
    """Live-follow view of the most recent errors."""
    console.print("[dim]Press Ctrl+C to exit live tail...[/dim]\n")

    try:
        with Live(console=console, refresh_per_second=1 / refresh_interval) as live:
            while True:
                records = storage.get_recent(limit=10)
                layout = Layout()

                table = Table(
                    title="Live Error Feed",
                    show_header=True,
                    header_style="bold magenta",
                )
                table.add_column("Time", style="dim", width=19)
                table.add_column("Script", style="cyan", width=25)
                table.add_column("Category", style="yellow", width=18)
                table.add_column("Type", style="red", width=18)
                table.add_column("Message")

                for rec in records:
                    if rec.exit_code != 0:
                        msg = (rec.message or "")[:40]
                        table.add_row(
                            rec.timestamp[11:19],
                            rec.script_name,
                            rec.category or "—",
                            rec.exception_type or "—",
                            msg,
                        )

                layout.update(
                    Panel(
                        table,
                        title="[bold cyan]pydebugger — Live Tail[/bold cyan]",
                        border_style="cyan",
                    )
                )
                live.update(layout)
    except KeyboardInterrupt:
        console.print("\n[dim]Live tail stopped.[/dim]")
