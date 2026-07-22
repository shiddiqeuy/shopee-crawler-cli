"""Seller analytics."""

from shopee_cli.analytics.models import ProductDistribution, SellerAnalysis
from shopee_cli.analytics.statistics import unique_count
from shopee_cli.collectors.models import SearchResult


def analyze_sellers(results: list[SearchResult]) -> SellerAnalysis:
    """Analyze seller-related visible fields."""
    return SellerAnalysis(
        unique_shops=unique_count(result.shop_name for result in results),
        mall_shops=sum(result.is_mall is True for result in results),
        preferred_shops=sum(result.is_preferred is True for result in results),
        advertisement_products=sum(
            result.is_advertisement is True for result in results
        ),
        organic_products=sum(result.is_advertisement is False for result in results),
    )


def analyze_distribution(results: list[SearchResult]) -> ProductDistribution:
    """Analyze product distribution by flags."""
    return ProductDistribution(
        mall=sum(result.is_mall is True for result in results),
        preferred=sum(result.is_preferred is True for result in results),
        advertisement=sum(result.is_advertisement is True for result in results),
        unknown=sum(
            result.is_mall is None
            or result.is_preferred is None
            or result.is_advertisement is None
            for result in results
        ),
    )
