"""Export summary statistic tests."""

from datetime import UTC, datetime

from shopee_cli.collectors.models import SearchResult
from shopee_cli.exports.summary_sheet import calculate_summary_stats


def _result(
    price: int | None = None,
    sold: int | None = None,
    rating: float | None = None,
    shop: str | None = None,
    location: str | None = None,
    ad: bool | None = None,
    mall: bool | None = None,
    preferred: bool | None = None,
) -> SearchResult:
    return SearchResult(
        rank=1,
        product_name="Product",
        product_url="https://shopee.co.id/product",
        price_min=price,
        sold_count=sold,
        rating=rating,
        shop_name=shop,
        location=location,
        is_advertisement=ad,
        is_mall=mall,
        is_preferred=preferred,
        collected_at=datetime.now(UTC),
    )


def test_calculates_product_and_price_statistics() -> None:
    """Price statistics ignore nulls and use price_min."""
    stats = calculate_summary_stats([_result(price=10000), _result(price=30000)])

    assert stats.total_products == 2
    assert stats.minimum_price == 10000
    assert stats.maximum_price == 30000
    assert stats.average_minimum_price == 20000


def test_calculates_median_price_for_odd_rows() -> None:
    """Odd medians are deterministic."""
    stats = calculate_summary_stats(
        [_result(price=10000), _result(price=50000), _result(price=30000)]
    )

    assert stats.median_minimum_price == 30000


def test_calculates_median_price_for_even_rows() -> None:
    """Even medians are deterministic averages."""
    stats = calculate_summary_stats([_result(price=10000), _result(price=30000)])

    assert stats.median_minimum_price == 20000


def test_ignores_null_prices_and_sold_values() -> None:
    """Missing numeric values are not treated as zero."""
    stats = calculate_summary_stats(
        [_result(price=None, sold=None), _result(price=50, sold=10)]
    )

    assert stats.products_with_price == 1
    assert stats.products_with_sold_data == 1
    assert stats.average_sold_count == 10


def test_calculates_rating_and_boolean_counts() -> None:
    """Ratings and explicit true booleans are counted."""
    stats = calculate_summary_stats(
        [
            _result(rating=4.0, ad=True, mall=True, preferred=False),
            _result(rating=5.0, ad=None, mall=False, preferred=True),
        ]
    )

    assert stats.average_rating == 4.5
    assert stats.advertisement_count == 1
    assert stats.mall_product_count == 1
    assert stats.preferred_product_count == 1
    assert stats.unknown_advertisement_status == 1


def test_counts_missing_values_and_unique_fields() -> None:
    """Data quality counts and unique text fields are calculated."""
    stats = calculate_summary_stats(
        [
            _result(shop=" Shop A ", location="Jakarta"),
            _result(shop="Shop A", location=None),
        ]
    )

    assert stats.unique_shops == 1
    assert stats.unique_locations == 1
    assert stats.missing_location == 1


def test_handles_zero_result_jobs() -> None:
    """Zero-result snapshots produce empty-safe stats."""
    stats = calculate_summary_stats([])

    assert stats.total_products == 0
    assert stats.minimum_price is None
    assert stats.average_rating is None
