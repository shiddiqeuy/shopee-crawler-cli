"""Analytics engine tests."""

from datetime import UTC, datetime

from shopee_cli.analytics.engine import analyze_snapshot
from shopee_cli.browser.models import BrowserMode
from shopee_cli.collectors.models import (
    SearchJob,
    SearchJobStatus,
    SearchResult,
    SearchSortMode,
)


def _job(collected_count: int = 3) -> SearchJob:
    return SearchJob(
        job_id="srch_test",
        keyword="kopi",
        requested_limit=50,
        collected_count=collected_count,
        browser_mode=BrowserMode.MAIN,
        sort_mode=SearchSortMode.RELEVANCE,
        source_url="https://shopee.co.id/search?keyword=kopi",
        status=SearchJobStatus.COMPLETED,
        started_at=datetime.now(UTC),
    )


def _result(
    price: int | None,
    sold: int | None,
    rating: float | None,
    location: str | None,
) -> SearchResult:
    return SearchResult(
        rank=1,
        product_name="Product",
        product_url="https://shopee.co.id/product",
        price_min=price,
        sold_count=sold,
        rating=rating,
        shop_name="Shop",
        location=location,
        is_advertisement=False,
        is_mall=True,
        is_preferred=None,
        collected_at=datetime.now(UTC),
    )


def test_analyzes_snapshot_metrics_and_missing_values() -> None:
    """Analytics report is derived from stored records."""
    results = [
        _result(10000, 10, 4.0, "Jakarta"),
        _result(30000, None, 5.0, "Bandung"),
        _result(None, 30, None, "Jakarta"),
    ]

    report = analyze_snapshot(_job(), results)

    assert report.price.minimum == 10000
    assert report.price.maximum == 30000
    assert report.price.average == 20000
    assert report.sales.missing == 1
    assert report.rating.average == 4.5
    assert report.seller.unique_shops == 1
    assert report.location.top_locations[0] == ("Jakarta", 2)
    assert report.quality.missing_price == 1


def test_zero_product_dataset() -> None:
    """Empty snapshots produce null-safe analytics."""
    report = analyze_snapshot(_job(collected_count=0), [])

    assert report.total_products == 0
    assert report.price.average is None
    assert report.location.top_locations == []


def test_duplicate_products_removed_metric() -> None:
    """Duplicate removal is traceable from job count versus stored rows."""
    report = analyze_snapshot(_job(collected_count=3), [_result(1, 1, 1, "A")])

    assert report.quality.duplicate_products_removed == 2
