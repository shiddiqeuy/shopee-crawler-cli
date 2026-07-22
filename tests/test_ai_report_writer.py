"""AI report writer tests."""

from datetime import UTC, datetime

import pytest

from shopee_cli.ai.models import AIProviderName
from shopee_cli.ai.report_writer import write_markdown_report
from shopee_cli.analytics.engine import analyze_snapshot
from shopee_cli.browser.models import BrowserMode
from shopee_cli.collectors.models import SearchJob, SearchJobStatus, SearchSortMode


def _report():
    job = SearchJob(
        job_id="srch_test",
        keyword="kopi arabika",
        requested_limit=10,
        collected_count=0,
        browser_mode=BrowserMode.MAIN,
        sort_mode=SearchSortMode.RELEVANCE,
        source_url="https://shopee.co.id/search?keyword=kopi",
        status=SearchJobStatus.COMPLETED,
        started_at=datetime(2026, 7, 22, tzinfo=UTC),
    )
    return analyze_snapshot(job, [])


def test_markdown_writer_includes_metadata(tmp_path) -> None:
    """Markdown reports include required metadata."""
    path = tmp_path / "report.md"

    written = write_markdown_report(
        markdown="# Market Insight\n\n## Executive Summary\nTest",
        report=_report(),
        provider=AIProviderName.OPENAI,
        model="test-model",
        output_path=path,
        generated_at=datetime(2026, 7, 22, 10, 0),
    )

    content = written.read_text(encoding="utf-8")
    assert "job_id: srch_test" in content
    assert "provider: openai" in content
    assert "model: test-model" in content


def test_markdown_writer_rejects_non_markdown_output(tmp_path) -> None:
    """Reports must be Markdown files."""
    with pytest.raises(ValueError):
        write_markdown_report(
            markdown="# Market Insight",
            report=_report(),
            provider=AIProviderName.OPENAI,
            model="test-model",
            output_path=tmp_path / "report.txt",
        )
