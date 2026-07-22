"""Analytics engine."""

from shopee_cli.analytics.location import analyze_locations
from shopee_cli.analytics.models import AnalyticsReport
from shopee_cli.analytics.price import analyze_prices
from shopee_cli.analytics.quality import analyze_quality
from shopee_cli.analytics.rating import analyze_ratings
from shopee_cli.analytics.sales import analyze_sales
from shopee_cli.analytics.seller import analyze_distribution, analyze_sellers
from shopee_cli.collectors.models import SearchJob, SearchResult


def analyze_snapshot(job: SearchJob, results: list[SearchResult]) -> AnalyticsReport:
    """Analyze one historical search snapshot without side effects."""
    return AnalyticsReport(
        job=job,
        total_products=len(results),
        price=analyze_prices(results),
        sales=analyze_sales(results),
        rating=analyze_ratings(results),
        seller=analyze_sellers(results),
        location=analyze_locations(results),
        distribution=analyze_distribution(results),
        quality=analyze_quality(results, job.collected_count),
    )
