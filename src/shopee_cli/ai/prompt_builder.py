"""AI insight prompt and compact JSON builder."""

import json
from datetime import datetime

from shopee_cli.ai.models import InsightPrompt
from shopee_cli.analytics.models import AnalyticsReport

SYSTEM_PROMPT = """You are a Market Intelligence Analyst.
Use ONLY supplied JSON.
Never invent statistics.
Never estimate missing data.
Never create numbers.
If data is unavailable, explicitly state it.
Always separate: Observation, Interpretation, Limitation.
Keep Executive Summary under 200 words.
Do not calculate averages, medians, percentages, quartiles, or rankings.
""".strip()

USER_PROMPT_TEMPLATE = """Create a Markdown market insight report from this JSON only.

Required sections:
# Market Insight
## Executive Summary
## Price Observation
## Competition Observation
## Seller Observation
## Location Observation
## Data Quality
## Overall Insight
## Limitation

Every observation must reference supplied statistics.
Interpretations must use cautious language such as MAY or COULD.
Always mention these limitations: snapshot based, search result only,
not full marketplace, no transaction data.

JSON:
{analytics_json}
""".strip()


def build_prompt(report: AnalyticsReport) -> InsightPrompt:
    """Build provider-ready prompt from analytics report."""
    analytics_json = serialize_analytics_report(report)
    return InsightPrompt(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=USER_PROMPT_TEMPLATE.format(analytics_json=analytics_json),
        analytics_json=analytics_json,
    )


def serialize_analytics_report(report: AnalyticsReport) -> str:
    """Serialize analytics into compact JSON for AI providers."""
    payload = {
        "metadata": {
            "job_id": report.job.job_id,
            "keyword": report.job.keyword,
            "search_date": _datetime_value(
                report.job.finished_at or report.job.started_at
            ),
            "browser_mode": report.job.browser_mode.value,
            "sort_mode": report.job.sort_mode.value,
            "collected_products": report.job.collected_count,
        },
        "market_summary": {
            "total_products": report.total_products,
        },
        "price_statistics": {
            "minimum": report.price.minimum,
            "maximum": report.price.maximum,
            "average": report.price.average,
            "median": report.price.median,
            "range": report.price.price_range,
            "products_with_price": report.price.count,
            "missing_price": report.price.missing,
            "q1": report.price.q1,
            "q3": report.price.q3,
        },
        "sales_statistics": {
            "minimum": report.sales.minimum,
            "maximum": report.sales.maximum,
            "average": report.sales.average,
            "median": report.sales.median,
            "products_with_sold_data": report.sales.count,
            "missing_sold_data": report.sales.missing,
        },
        "seller_statistics": {
            "unique_shops": report.seller.unique_shops,
            "mall_shops": report.seller.mall_shops,
            "preferred_shops": report.seller.preferred_shops,
            "advertisement_products": report.seller.advertisement_products,
            "organic_products": report.seller.organic_products,
        },
        "location_statistics": {
            "unique_locations": report.location.unique_locations,
            "top_locations": report.location.top_locations,
        },
        "quality_metrics": {
            "missing_price": report.quality.missing_price,
            "missing_rating": report.quality.missing_rating,
            "missing_sold": report.quality.missing_sold,
            "missing_shop": report.quality.missing_shop,
            "missing_location": report.quality.missing_location,
            "duplicate_products_removed": report.quality.duplicate_products_removed,
        },
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _datetime_value(value: datetime) -> str:
    return value.isoformat()
