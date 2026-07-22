"""AI insight command."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from shopee_cli.ai.engine import AIInsightEngine
from shopee_cli.ai.exceptions import AIInsightError
from shopee_cli.ai.models import AIProviderName, InsightResult
from shopee_cli.config.settings import get_settings
from shopee_cli.database.search_repository import SearchRepository
from shopee_cli.logging.logger import get_logger

console = Console()
logger = get_logger(__name__)


def run_insight(
    job_id: Annotated[
        str | None,
        typer.Option("--job-id", help="Generate insight for an exact completed job."),
    ] = None,
    keyword: Annotated[
        str | None,
        typer.Option(
            "--keyword", help="Generate insight for latest completed keyword."
        ),
    ] = None,
    provider: Annotated[
        AIProviderName,
        typer.Option("--provider", help="AI provider to use."),
    ] = AIProviderName.OPENAI,
    output: Annotated[
        Path | None,
        typer.Option("--output", help="Markdown output path."),
    ] = None,
) -> None:
    """Generate an AI market insight report from analytics JSON."""
    engine = AIInsightEngine(SearchRepository(get_settings()))
    try:
        result = engine.generate(
            job_id=job_id,
            keyword=keyword,
            provider_name=provider,
            output_path=output,
        )
    except (AIInsightError, LookupError, ValueError) as error:
        logger.warning("ai_insight_failed", provider=provider.value, error=str(error))
        console.print(str(error))
        _print_hint(error)
        raise typer.Exit(1) from error

    _print_result(result)


def _print_result(result: InsightResult) -> None:
    table = Table(title="AI Insight Completed")
    table.add_column("Item", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    table.add_row("Provider", result.provider.value)
    table.add_row("Model", result.model)
    table.add_row("Output File", str(result.output_path))
    table.add_row("Generation Duration", f"{result.duration_seconds:.2f}s")
    console.print(table)


def _print_hint(error: Exception) -> None:
    message = str(error)
    if "API_KEY" in message:
        console.print("Set the required environment variable, then retry.")
    if "No completed" in message:
        console.print("Run a search first:")
        console.print('shopee search "kopi arabika"')
