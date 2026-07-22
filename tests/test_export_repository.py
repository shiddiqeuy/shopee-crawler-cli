"""Export search repository read-method tests."""

from datetime import UTC, datetime

from shopee_cli.browser.models import BrowserMode
from shopee_cli.collectors.models import (
    SearchJobStatus,
    SearchRequest,
    SearchResult,
    SearchSortMode,
)
from shopee_cli.config.settings import Settings
from shopee_cli.database.connection import open_database
from shopee_cli.database.search_repository import SearchRepository


def _settings(tmp_path) -> Settings:
    return Settings(database_dir=tmp_path, database_file_name="export.duckdb")


def _request(keyword: str) -> SearchRequest:
    return SearchRequest(
        keyword=keyword,
        requested_limit=10,
        browser_mode=BrowserMode.MAIN,
        sort_mode=SearchSortMode.RELEVANCE,
        max_scrolls=2,
        source_url=f"https://shopee.co.id/search?keyword={keyword}",
    )


def _result(rank: int = 1) -> SearchResult:
    return SearchResult(
        product_id=str(rank),
        rank=rank,
        product_name=f"Product {rank}",
        product_url=f"https://shopee.co.id/Product-i.1.{rank}",
        collected_at=datetime.now(UTC),
    )


def _job(repository: SearchRepository, keyword: str, status: SearchJobStatus):
    job = repository.create_job(_request(keyword))
    if status in {SearchJobStatus.COMPLETED, SearchJobStatus.PARTIAL}:
        repository.save_results(job.job_id, [_result()])
        return repository.update_job_status(job.job_id, status, collected_count=1)
    return repository.update_job_status(
        job.job_id, status, error_message="not exportable"
    )


def test_selects_latest_completed_job(tmp_path) -> None:
    """Latest completed job can be selected for export."""
    repository = SearchRepository(_settings(tmp_path))
    _job(repository, "kopi lama", SearchJobStatus.COMPLETED)
    latest = _job(repository, "kopi baru", SearchJobStatus.COMPLETED)

    assert repository.get_latest_exportable_job().job_id == latest.job_id


def test_selects_latest_partial_job(tmp_path) -> None:
    """Partial jobs are exportable."""
    repository = SearchRepository(_settings(tmp_path))
    partial = _job(repository, "kopi", SearchJobStatus.PARTIAL)

    assert repository.get_latest_exportable_job().job_id == partial.job_id


def test_ignores_running_and_failed_jobs(tmp_path) -> None:
    """Non-exportable jobs are ignored."""
    repository = SearchRepository(_settings(tmp_path))
    completed = _job(repository, "kopi", SearchJobStatus.COMPLETED)
    repository.create_job(_request("running"))
    _job(repository, "failed", SearchJobStatus.FAILED)

    assert repository.get_latest_exportable_job().job_id == completed.job_id


def test_selects_exact_job_id(tmp_path) -> None:
    """Exact job ID lookup returns that job."""
    repository = SearchRepository(_settings(tmp_path))
    job = _job(repository, "kopi", SearchJobStatus.COMPLETED)

    assert repository.get_search_job(job.job_id).job_id == job.job_id


def test_selects_latest_job_by_keyword(tmp_path) -> None:
    """Keyword lookup returns latest matching exportable job."""
    repository = SearchRepository(_settings(tmp_path))
    _job(repository, "kopi arabika", SearchJobStatus.COMPLETED)
    latest = _job(repository, "kopi arabika", SearchJobStatus.PARTIAL)
    _job(repository, "teh", SearchJobStatus.COMPLETED)

    selected = repository.get_latest_exportable_job_by_keyword("kopi arabika")

    assert selected.job_id == latest.job_id


def test_preserves_rank_order_and_does_not_mutate_rows(tmp_path) -> None:
    """Export reads preserve source snapshot rows."""
    settings = _settings(tmp_path)
    repository = SearchRepository(settings)
    job = repository.create_job(_request("kopi"))
    repository.save_results(job.job_id, [_result(2), _result(1)])
    repository.update_job_status(
        job.job_id, SearchJobStatus.COMPLETED, collected_count=2
    )

    before = _counts(settings)
    results = repository.get_search_results(job.job_id)
    after = _counts(settings)

    assert [result.rank for result in results] == [1, 2]
    assert before == after


def _counts(settings: Settings) -> tuple[int, int]:
    with open_database(settings) as connection:
        jobs = connection.execute("SELECT COUNT(*) FROM search_jobs").fetchone()[0]
        results = connection.execute("SELECT COUNT(*) FROM search_results").fetchone()[
            0
        ]
    return jobs, results
