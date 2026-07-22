"""Export commands."""

import os
import platform
import subprocess
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from shopee_cli.config.settings import get_settings
from shopee_cli.database.search_repository import SearchRepository
from shopee_cli.exports.excel_exporter import ExcelExporter
from shopee_cli.exports.exceptions import ExportError, ExportOpenError
from shopee_cli.logging.logger import get_logger

export_app = typer.Typer(help="Export stored search snapshots.")
console = Console()
logger = get_logger(__name__)


@export_app.command("excel")
def export_excel(
    job_id: Annotated[
        str | None,
        typer.Option("--job-id", help="Export an exact search job ID."),
    ] = None,
    keyword: Annotated[
        str | None,
        typer.Option("--keyword", help="Export latest snapshot for a keyword."),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option("--output", help="Custom .xlsx output path."),
    ] = None,
    open_file: Annotated[
        bool,
        typer.Option("--open", help="Open the generated workbook after export."),
    ] = False,
) -> None:
    """Export a search snapshot to an Excel workbook."""
    settings = get_settings()
    exporter = ExcelExporter(settings=settings)
    try:
        result = exporter.export(job_id=job_id, keyword=keyword, output_path=output)
    except ExportError as error:
        logger.warning("excel_export_failed", error=str(error))
        console.print(str(error))
        _print_export_hint(error)
        raise typer.Exit(1) from error

    _print_export_result(result)
    if open_file:
        try:
            _open_path(result.output_path)
        except ExportOpenError as error:
            logger.warning("excel_export_open_failed", error=str(error))
            console.print(
                "The report was created, but it could not be opened automatically."
            )
            console.print("Open it manually using the path above.")


@export_app.command("jobs")
def list_export_jobs(
    limit: Annotated[
        int,
        typer.Option("--limit", help="Maximum recent exportable jobs to show."),
    ] = 20,
) -> None:
    """List recent completed or partial search jobs."""
    if limit < 1 or limit > 100:
        console.print("Limit must be between 1 and 100.")
        raise typer.Exit(2)

    repository = SearchRepository(get_settings())
    jobs = repository.list_exportable_jobs(limit=limit)
    if not jobs:
        console.print("No completed or partial search job was found.")
        console.print("Run a search first:")
        console.print('shopee search "kopi arabika"')
        return

    table = Table(title="Exportable Search Jobs")
    table.add_column("Job ID", style="cyan", no_wrap=True)
    table.add_column("Keyword")
    table.add_column("Status")
    table.add_column("Products", justify="right")
    table.add_column("Started At")
    table.add_column("Finished At")
    table.add_column("Browser Mode")
    table.add_column("Sort Mode")
    for job in jobs:
        table.add_row(
            job.job_id,
            job.keyword,
            job.status.value,
            str(job.collected_count),
            _format_datetime(job.started_at),
            _format_datetime(job.finished_at),
            job.browser_mode.value,
            job.sort_mode.value,
        )
    console.print(table)


def _print_export_result(result: object) -> None:
    table = Table(title="Excel Export Completed")
    table.add_column("Item", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    table.add_row("Sheets", str(result.sheet_count))
    table.add_row("Products", str(result.product_count))
    table.add_row("File", str(result.output_path))
    console.print(table)


def _print_export_hint(error: ExportError) -> None:
    message = str(error)
    if "not found" in message or "No completed" in message:
        console.print("List available jobs with:")
        console.print("shopee export jobs")
    if "already exists" in message:
        console.print("Choose another path using:")
        console.print("shopee export excel --output data/exports/report-v2.xlsx")


def _open_path(path: Path) -> None:
    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(path)  # type: ignore[attr-defined]
            return
        if system == "Darwin":
            subprocess.run(["open", str(path)], check=True)
            return
        subprocess.run(["xdg-open", str(path)], check=True)
    except (OSError, subprocess.CalledProcessError) as error:
        msg = f"Excel report could not be opened automatically: {path}"
        raise ExportOpenError(msg) from error


def _format_datetime(value: object) -> str:
    if value is None:
        return ""
    return str(value)
