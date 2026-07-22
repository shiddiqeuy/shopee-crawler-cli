"""AI insight engine tests."""

from datetime import UTC, datetime

from shopee_cli.ai.engine import AIInsightEngine
from shopee_cli.ai.models import AIProviderName, InsightRequest, InsightResponse
from shopee_cli.browser.models import BrowserMode
from shopee_cli.collectors.models import (
    SearchJob,
    SearchJobStatus,
    SearchResult,
    SearchSortMode,
)


class FakeRepository:
    """Read-only repository fake."""

    def __init__(self) -> None:
        self.writes = 0
        self.job = SearchJob(
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

    def get_latest_completed_job(self):
        return self.job

    def get_latest_completed_job_by_keyword(self, keyword: str):
        return self.job

    def get_search_job(self, job_id: str):
        return self.job

    def get_search_results(self, job_id: str):
        return [
            SearchResult(
                rank=1,
                product_name="Kopi",
                product_url="https://shopee.co.id/Kopi-i.1.1",
                price_min=25000,
                sold_count=100,
                collected_at=datetime(2026, 7, 22, tzinfo=UTC),
            )
        ]


class FakeProvider:
    """Provider fake that records prompt shape."""

    name = AIProviderName.OPENAI
    default_model = "fake-model"

    def __init__(self) -> None:
        self.request: InsightRequest | None = None

    def generate(self, request: InsightRequest) -> InsightResponse:
        self.request = request
        return InsightResponse(
            markdown="# Market Insight\n\n## Executive Summary\nObservation only.",
            provider=self.name,
            model=request.model,
        )


def test_ai_engine_generates_markdown_without_database_writes(tmp_path) -> None:
    """Engine reads analytics, sends JSON prompt, and writes Markdown."""
    repository = FakeRepository()
    provider = FakeProvider()
    output = tmp_path / "insight.md"

    result = AIInsightEngine(repository, provider=provider).generate(output_path=output)

    assert output.exists()
    assert result.provider == AIProviderName.OPENAI
    assert provider.request is not None
    assert provider.request.prompt.analytics_json.startswith("{")
    assert repository.writes == 0
