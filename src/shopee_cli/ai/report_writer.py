"""Markdown report writer."""

import re
import unicodedata
from datetime import datetime
from pathlib import Path

from shopee_cli.ai.models import AIProviderName
from shopee_cli.analytics.models import AnalyticsReport


def write_markdown_report(
    markdown: str,
    report: AnalyticsReport,
    provider: AIProviderName,
    model: str,
    output_path: Path | None = None,
    generated_at: datetime | None = None,
) -> Path:
    """Write an insight Markdown report to disk."""
    created_at = generated_at or datetime.now()
    path = output_path or _default_output_path(report.job.keyword)
    if path.suffix.lower() != ".md":
        msg = "Insight output path must end with .md."
        raise ValueError(msg)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = _with_metadata(
        markdown=markdown,
        report=report,
        provider=provider,
        model=model,
        generated_at=created_at,
    )
    path.write_text(content, encoding="utf-8")
    return path


def _default_output_path(keyword: str) -> Path:
    return Path("reports") / f"{_slugify(keyword)}-insight.md"


def _with_metadata(
    markdown: str,
    report: AnalyticsReport,
    provider: AIProviderName,
    model: str,
    generated_at: datetime,
) -> str:
    metadata = "\n".join(
        [
            "---",
            f"generated_at: {generated_at.isoformat()}",
            f"job_id: {report.job.job_id}",
            f"keyword: {report.job.keyword}",
            f"provider: {provider.value}",
            f"model: {model}",
            "---",
            "",
        ]
    )
    return f"{metadata}{markdown.strip()}\n"


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip().lower())
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return cleaned or "shopee-insight"
