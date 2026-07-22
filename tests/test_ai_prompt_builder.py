"""AI prompt builder tests."""

import json
from datetime import UTC, datetime

from shopee_cli.ai.prompt_builder import build_prompt, serialize_analytics_report
from shopee_cli.analytics.engine import analyze_snapshot
from shopee_cli.browser.models import BrowserMode
from shopee_cli.collectors.models import (
    SearchJob,
    SearchJobStatus,
    SearchResult,
    SearchSortMode,
)


def _report():
    job = SearchJob(
        job_id="srch_test",
        keyword="kopi",
        requested_limit=10,
        collected_count=1,
        browser_mode=BrowserMode.MAIN,
        sort_mode=SearchSortMode.RELEVANCE,
        source_url="https://shopee.co.id/search?keyword=kopi",
        status=SearchJobStatus.COMPLETED,
        started_at=datetime(2026, 7, 22, tzinfo=UTC),
    )
    results = [
        SearchResult(
            rank=1,
            product_name="Kopi",
            product_url="https://shopee.co.id/Kopi-i.1.1",
            price_min=25000,
            sold_count=1200,
            rating=4.9,
            shop_name="Shop",
            location="Jakarta",
            is_advertisement=False,
            collected_at=datetime(2026, 7, 22, tzinfo=UTC),
        )
    ]
    return analyze_snapshot(job, results)


def test_json_serialization_contains_only_structured_analytics() -> None:
    """AI receives compact structured analytics JSON only."""
    payload = json.loads(serialize_analytics_report(_report()))

    assert set(payload) == {
        "metadata",
        "market_summary",
        "price_statistics",
        "sales_statistics",
        "seller_statistics",
        "location_statistics",
        "quality_metrics",
    }
    assert "raw_sql" not in payload
    assert "html" not in payload


def test_prompt_enforces_no_metric_calculation() -> None:
    """Prompt tells the model to interpret only supplied JSON."""
    prompt = build_prompt(_report())

    assert "Never invent statistics" in prompt.system_prompt
    assert "Do not calculate averages" in prompt.system_prompt
    assert prompt.analytics_json in prompt.user_prompt
