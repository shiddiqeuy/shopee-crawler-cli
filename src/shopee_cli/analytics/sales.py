"""Sales analytics."""

from shopee_cli.analytics.models import NumericSummary
from shopee_cli.analytics.statistics import average, median, non_null
from shopee_cli.collectors.models import SearchResult


def analyze_sales(results: list[SearchResult]) -> NumericSummary:
    """Analyze normalized sold_count values."""
    sold_counts = non_null(result.sold_count for result in results)
    return NumericSummary(
        minimum=min(sold_counts) if sold_counts else None,
        maximum=max(sold_counts) if sold_counts else None,
        average=average(sold_counts),
        median=median(sold_counts),
        count=len(sold_counts),
        missing=sum(result.sold_count is None for result in results),
    )
