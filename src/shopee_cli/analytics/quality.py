"""Data quality analytics."""

from shopee_cli.analytics.models import QualityMetrics
from shopee_cli.collectors.models import SearchResult


def analyze_quality(
    results: list[SearchResult], collected_count: int
) -> QualityMetrics:
    """Analyze missing values and duplicate-removal signal."""
    return QualityMetrics(
        missing_price=sum(result.price_min is None for result in results),
        missing_rating=sum(result.rating is None for result in results),
        missing_sold=sum(result.sold_count is None for result in results),
        missing_shop=sum(not _has_text(result.shop_name) for result in results),
        missing_location=sum(not _has_text(result.location) for result in results),
        duplicate_products_removed=max(collected_count - len(results), 0),
    )


def _has_text(value: str | None) -> bool:
    return bool(value and value.strip())
