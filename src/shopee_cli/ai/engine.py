"""AI insight orchestration."""

from pathlib import Path
from time import perf_counter

from shopee_cli.ai.models import AIProviderName, InsightRequest, InsightResult
from shopee_cli.ai.prompt_builder import build_prompt
from shopee_cli.ai.provider import AIProvider, create_provider
from shopee_cli.ai.report_writer import write_markdown_report
from shopee_cli.analytics.engine import analyze_snapshot
from shopee_cli.collectors.models import SearchJob, SearchJobStatus
from shopee_cli.database.search_repository import SearchRepository


class AIInsightEngine:
    """Generate AI insight reports from existing analytics only."""

    def __init__(
        self,
        repository: SearchRepository,
        provider: AIProvider | None = None,
    ) -> None:
        self._repository = repository
        self._provider = provider

    def generate(
        self,
        job_id: str | None = None,
        keyword: str | None = None,
        provider_name: AIProviderName = AIProviderName.OPENAI,
        output_path: Path | None = None,
    ) -> InsightResult:
        """Generate a Markdown insight report."""
        if job_id and keyword:
            msg = "Use either --job-id or --keyword, not both."
            raise ValueError(msg)
        job = self._select_job(job_id=job_id, keyword=keyword)
        results = self._repository.get_search_results(job.job_id)
        analytics_report = analyze_snapshot(job, results)
        provider = self._provider or create_provider(provider_name)
        model = provider.default_model
        prompt = build_prompt(analytics_report)
        request = InsightRequest(provider=provider.name, model=model, prompt=prompt)
        started_at = perf_counter()
        response = provider.generate(request)
        duration_seconds = perf_counter() - started_at
        path = write_markdown_report(
            markdown=response.markdown,
            report=analytics_report,
            provider=response.provider,
            model=response.model,
            output_path=output_path,
        )
        return InsightResult(
            report=analytics_report,
            provider=response.provider,
            model=response.model,
            output_path=path,
            duration_seconds=duration_seconds,
            markdown=response.markdown,
        )

    def _select_job(self, job_id: str | None, keyword: str | None) -> SearchJob:
        if job_id:
            job = self._repository.get_search_job(job_id)
        elif keyword:
            job = self._repository.get_latest_completed_job_by_keyword(keyword.strip())
        else:
            job = self._repository.get_latest_completed_job()
        if job is None:
            msg = "No completed search job was found."
            raise LookupError(msg)
        if job.status != SearchJobStatus.COMPLETED:
            msg = (
                f'Search job {job.job_id} has status "{job.status.value}" '
                "and cannot be analyzed."
            )
            raise ValueError(msg)
        return job
