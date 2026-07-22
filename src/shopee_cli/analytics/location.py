"""Location analytics."""

from collections import Counter

from shopee_cli.analytics.models import LocationAnalysis
from shopee_cli.analytics.statistics import unique_count
from shopee_cli.collectors.models import SearchResult


def analyze_locations(results: list[SearchResult]) -> LocationAnalysis:
    """Analyze visible product locations."""
    locations = [
        result.location.strip()
        for result in results
        if result.location and result.location.strip()
    ]
    return LocationAnalysis(
        unique_locations=unique_count(locations),
        top_locations=Counter(locations).most_common(10),
    )
