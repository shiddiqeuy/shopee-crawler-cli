"""Price analytics."""

from shopee_cli.analytics.models import PriceAnalysis
from shopee_cli.analytics.statistics import average, median, non_null, quartiles
from shopee_cli.collectors.models import SearchResult


def analyze_prices(results: list[SearchResult]) -> PriceAnalysis:
    """Analyze normalized price_min values."""
    prices = non_null(result.price_min for result in results)
    q1, q2, q3 = quartiles(prices)
    minimum = min(prices) if prices else None
    maximum = max(prices) if prices else None
    return PriceAnalysis(
        minimum=minimum,
        maximum=maximum,
        average=average(prices),
        median=median(prices),
        count=len(prices),
        missing=sum(result.price_min is None for result in results),
        price_range=(maximum - minimum)
        if minimum is not None and maximum is not None
        else None,
        q1=q1,
        q3=q3,
    )
