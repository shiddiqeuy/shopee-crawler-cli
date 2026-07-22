"""Search collection command."""

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from shopee_cli.browser.exceptions import (
    BrowserConnectionError,
    InvalidBrowserModeError,
)
from shopee_cli.browser.manager import BrowserManager
from shopee_cli.browser.models import BrowserMode
from shopee_cli.collectors.exceptions import (
    InvalidKeywordError,
    SearchCollectorError,
    SearchPersistenceError,
)
from shopee_cli.collectors.models import SearchJobStatus, SearchSortMode
from shopee_cli.collectors.search_collector import (
    SearchCollector,
    create_search_request,
    validate_limit,
    validate_max_scrolls,
)
from shopee_cli.config.settings import get_settings
from shopee_cli.database.search_repository import SearchRepository
from shopee_cli.logging.logger import get_logger

console = Console()
logger = get_logger(__name__)


def run_search(
    keyword: Annotated[str, typer.Argument(help="Shopee search keyword.")],
    limit: Annotated[
        int,
        typer.Option("--limit", help="Maximum products to collect, 1-200."),
    ] = 50,
    mode: Annotated[
        BrowserMode | None,
        typer.Option("--mode", help="Temporarily override browser mode."),
    ] = None,
    sort: Annotated[
        SearchSortMode,
        typer.Option("--sort", help="Search sort mode."),
    ] = SearchSortMode.RELEVANCE,
    max_scrolls: Annotated[
        int,
        typer.Option(
            "--max-scrolls",
            help="Maximum conservative scroll attempts, 1-30.",
        ),
    ] = 10,
) -> None:
    """Collect visible Shopee search-result cards into DuckDB."""
    settings = get_settings()
    selected_mode = mode or settings.browser_mode
    repository = SearchRepository(settings)
    job_id: str | None = None

    try:
        validate_limit(limit)
        validate_max_scrolls(max_scrolls)
        request = create_search_request(
            keyword=keyword,
            limit=limit,
            browser_mode=selected_mode,
            sort_mode=sort,
            max_scrolls=max_scrolls,
        )
        job = repository.create_job(request)
        job_id = job.job_id
        _print_start(
            request.keyword,
            request.browser_mode.value,
            request.requested_limit,
        )

        manager = BrowserManager(settings=settings, mode=selected_mode)
        try:
            with console.status("Collecting visible Shopee search results..."):
                manager.connect()
                collection = SearchCollector(manager).collect(request)
                completed_job = repository.complete_job(job.job_id, collection)
        finally:
            manager.disconnect()

        _print_summary(completed_job, str(settings.database_path))
    except (InvalidKeywordError, ValueError, InvalidBrowserModeError) as error:
        console.print(str(error))
        raise typer.Exit(2) from error
    except BrowserConnectionError as error:
        logger.warning("search_browser_connection_failed", error=str(error))
        _mark_failed(repository, job_id, str(error))
        console.print(str(error))
        raise typer.Exit(1) from error
    except SearchPersistenceError as error:
        logger.error("search_persistence_failed", error=str(error))
        console.print(str(error))
        raise typer.Exit(1) from error
    except SearchCollectorError as error:
        logger.warning("search_collection_failed", error=str(error))
        _mark_failed(repository, job_id, str(error))
        console.print(str(error))
        if "verification" in str(error).lower() or "login" in str(error).lower():
            console.print("Complete the manual step in the browser, then rerun search.")
        raise typer.Exit(1) from error


def _mark_failed(
    repository: SearchRepository,
    job_id: str | None,
    message: str,
) -> None:
    if job_id is None:
        return
    repository.update_job_status(
        job_id=job_id,
        status=SearchJobStatus.FAILED,
        error_message=message,
    )


def _print_start(keyword: str, browser_mode: str, target: int) -> None:
    table = Table(title="Search Collection")
    table.add_column("Item", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    table.add_row("Keyword", keyword)
    table.add_row("Browser Mode", browser_mode)
    table.add_row("Target", f"{target} products")
    console.print(table)


def _print_summary(job: object, database_path: str) -> None:
    table = Table(title="Search Completed")
    table.add_column("Item", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    table.add_row("Job ID", job.job_id)
    table.add_row("Keyword", job.keyword)
    table.add_row("Products", str(job.collected_count))
    table.add_row("Browser Mode", job.browser_mode.value)
    table.add_row("Status", job.status.value)
    table.add_row("Database", database_path)
    console.print(table)
