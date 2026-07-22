"""Analytics command."""

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from shopee_cli.analytics.engine import analyze_snapshot
from shopee_cli.analytics.models import AnalyticsReport
from shopee_cli.collectors.models import SearchJobStatus
from shopee_cli.config.settings import get_settings
from shopee_cli.database.search_repository import SearchRepository
from shopee_cli.logging.logger import get_logger

console = Console()
logger = get_logger(__name__)


def run_analytics(
    job_id: Annotated[
        str | None,
        typer.Option("--job-id", help="Analyze an exact completed search job ID."),
    ] = None,
    keyword: Annotated[
        str | None,
        typer.Option(
            "--keyword", help="Analyze latest completed snapshot for keyword."
        ),
    ] = None,
) -> None:
    """Analyze one completed Shopee search snapshot."""
    if job_id and keyword:
        console.print("Use either --job-id or --keyword, not both.")
        raise typer.Exit(2)

    repository = SearchRepository(get_settings())
    job = _select_job(repository, job_id=job_id, keyword=keyword)
    if job is None:
        console.print("No completed search job was found.")
        console.print("Run a search first:")
        console.print('shopee search "kopi arabika"')
        raise typer.Exit(1)
    if job.status != SearchJobStatus.COMPLETED:
        console.print(
            f'Search job {job.job_id} has status "{job.status.value}" '
            "and cannot be analyzed."
        )
        console.print("Choose a completed search job.")
        raise typer.Exit(1)

    results = repository.get_search_results(job.job_id)
    report = analyze_snapshot(job, results)
    _print_report(report)


def _select_job(
    repository: SearchRepository,
    job_id: str | None,
    keyword: str | None,
) -> object | None:
    if job_id:
        return repository.get_search_job(job_id)
    if keyword:
        return repository.get_latest_completed_job_by_keyword(keyword.strip())
    return repository.get_latest_completed_job()


def _print_report(report: AnalyticsReport) -> None:
    console.print(_report_info_table(report))
    console.print(_market_summary_table(report))
    console.print(_price_table(report))
    console.print(_sales_table(report))
    console.print(_rating_table(report))
    console.print(_seller_table(report))
    console.print(_location_table(report))
    console.print(_distribution_table(report))
    console.print(_quality_table(report))


def _base_table(title: str) -> Table:
    table = Table(title=title)
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    return table


def _report_info_table(report: AnalyticsReport) -> Table:
    table = _base_table("Report Information")
    table.add_row("Job ID", report.job.job_id)
    table.add_row("Keyword", report.job.keyword)
    table.add_row("Search Date", str(report.job.finished_at or report.job.started_at))
    table.add_row("Browser Mode", report.job.browser_mode.value)
    table.add_row("Collected Products", str(report.job.collected_count))
    return table


def _market_summary_table(report: AnalyticsReport) -> Table:
    table = _base_table("Market Summary")
    table.add_row("Total Products", str(report.total_products))
    table.add_row("Products With Price", str(report.price.count))
    table.add_row("Products With Sold Data", str(report.sales.count))
    table.add_row("Products With Rating", str(report.rating.count))
    return table


def _price_table(report: AnalyticsReport) -> Table:
    table = _base_table("Price Analysis")
    price = report.price
    rows = [
        ("Minimum Price", price.minimum),
        ("Maximum Price", price.maximum),
        ("Average Price", price.average),
        ("Median Price", price.median),
        ("Price Range", price.price_range),
        ("Products With Price", price.count),
        ("Missing Price", price.missing),
        ("Q1", price.q1),
        ("Median", price.median),
        ("Q3", price.q3),
    ]
    for label, value in rows:
        table.add_row(label, _value(value))
    return table


def _sales_table(report: AnalyticsReport) -> Table:
    return _numeric_table("Sales Analysis", report.sales, "Sold")


def _rating_table(report: AnalyticsReport) -> Table:
    return _numeric_table("Rating Analysis", report.rating, "Rating")


def _numeric_table(title: str, summary: object, label: str) -> Table:
    table = _base_table(title)
    table.add_row(f"Minimum {label}", _value(summary.minimum))
    table.add_row(f"Maximum {label}", _value(summary.maximum))
    table.add_row(f"Average {label}", _value(summary.average))
    table.add_row(f"Median {label}", _value(summary.median))
    table.add_row(f"Products With {label} Data", str(summary.count))
    table.add_row(f"Missing {label} Data", str(summary.missing))
    return table


def _seller_table(report: AnalyticsReport) -> Table:
    table = _base_table("Seller Analysis")
    seller = report.seller
    table.add_row("Unique Shops", str(seller.unique_shops))
    table.add_row("Mall Shops", str(seller.mall_shops))
    table.add_row("Preferred Shops", str(seller.preferred_shops))
    table.add_row("Advertisement Products", str(seller.advertisement_products))
    table.add_row("Organic Products", str(seller.organic_products))
    return table


def _location_table(report: AnalyticsReport) -> Table:
    table = _base_table("Location Analysis")
    table.add_row("Unique Locations", str(report.location.unique_locations))
    for location, count in report.location.top_locations:
        table.add_row(location, str(count))
    return table


def _distribution_table(report: AnalyticsReport) -> Table:
    table = _base_table("Product Distribution")
    distribution = report.distribution
    table.add_row("Mall", str(distribution.mall))
    table.add_row("Preferred", str(distribution.preferred))
    table.add_row("Advertisement", str(distribution.advertisement))
    table.add_row("Unknown", str(distribution.unknown))
    return table


def _quality_table(report: AnalyticsReport) -> Table:
    table = _base_table("Quality Metrics")
    quality = report.quality
    table.add_row("Missing Price", str(quality.missing_price))
    table.add_row("Missing Rating", str(quality.missing_rating))
    table.add_row("Missing Sold", str(quality.missing_sold))
    table.add_row("Missing Shop", str(quality.missing_shop))
    table.add_row("Missing Location", str(quality.missing_location))
    table.add_row("Duplicate Products Removed", str(quality.duplicate_products_removed))
    return table


def _value(value: object) -> str:
    if value is None:
        return "Unknown"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)
