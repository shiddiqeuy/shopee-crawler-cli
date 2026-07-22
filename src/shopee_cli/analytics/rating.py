"""Rating analytics."""

from shopee_cli.analytics.models import NumericSummary
from shopee_cli.analytics.statistics import average, median, non_null
from shopee_cli.collectors.models import SearchResult


def analyze_ratings(results: list[SearchResult]) -> NumericSummary:
    """Analyze visible rating values."""
    ratings = non_null(result.rating for result in results)
    return NumericSummary(
        minimum=min(ratings) if ratings else None,
        maximum=max(ratings) if ratings else None,
        average=average(ratings),
        median=median(ratings),
        count=len(ratings),
        missing=sum(result.rating is None for result in results),
    )
