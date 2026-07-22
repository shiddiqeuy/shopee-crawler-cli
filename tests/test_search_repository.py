"""Search repository tests."""

from datetime import UTC, datetime

from shopee_cli.browser.models import BrowserMode
from shopee_cli.collectors.models import (
    SearchCollection,
    SearchJobStatus,
    SearchRequest,
    SearchResult,
    SearchSortMode,
)
from shopee_cli.config.settings import Settings
from shopee_cli.database.connection import open_database
from shopee_cli.database.search_repository import SearchRepository


def _settings(tmp_path) -> Settings:
    return Settings(database_dir=tmp_path, database_file_name="test.duckdb")


def _request(keyword: str = "kopi") -> SearchRequest:
    return SearchRequest(
        keyword=keyword,
        requested_limit=10,
        browser_mode=BrowserMode.MAIN,
        sort_mode=SearchSortMode.RELEVANCE,
        max_scrolls=2,
        source_url=f"https://shopee.co.id/search?keyword={keyword}",
    )


def _result(name: str = "Kopi") -> SearchResult:
    return SearchResult(
        product_id="123",
        rank=1,
        product_name=name,
        product_url="https://shopee.co.id/Kopi-i.1.123",
        price_raw="Rp25.000",
        price_min=25000,
        price_max=25000,
        collected_at=datetime.now(UTC),
    )


def test_creates_schema_idempotently(tmp_path) -> None:
    """Search schema can be initialized repeatedly."""
    repository = SearchRepository(_settings(tmp_path))

    repository.initialize_schema()
    repository.initialize_schema()

    with open_database(_settings(tmp_path)) as connection:
        tables = {row[0] for row in connection.execute("SHOW TABLES").fetchall()}

    assert "search_jobs" in tables
    assert "search_results" in tables


def test_creates_search_job(tmp_path) -> None:
    """Repository creates a running search job."""
    repository = SearchRepository(_settings(tmp_path))

    job = repository.create_job(_request())

    assert job.job_id.startswith("srch_")
    assert job.status == SearchJobStatus.RUNNING


def test_saves_search_results_and_updates_completed_job(tmp_path) -> None:
    """Repository saves results and marks jobs completed."""
    settings = _settings(tmp_path)
    repository = SearchRepository(settings)
    job = repository.create_job(_request())
    collection = SearchCollection(
        request=_request(),
        results=[_result()],
        status=SearchJobStatus.COMPLETED,
    )

    completed = repository.complete_job(job.job_id, collection)

    assert completed.collected_count == 1
    assert completed.status == SearchJobStatus.COMPLETED
    with open_database(settings) as connection:
        result_count = connection.execute(
            "SELECT COUNT(*) FROM search_results"
        ).fetchone()[0]
    assert result_count == 1


def test_updates_failed_job(tmp_path) -> None:
    """Repository records failed job status and error message."""
    repository = SearchRepository(_settings(tmp_path))
    job = repository.create_job(_request())

    failed = repository.update_job_status(
        job.job_id,
        SearchJobStatus.FAILED,
        error_message="manual verification required",
    )

    assert failed.status == SearchJobStatus.FAILED
    assert failed.error_message == "manual verification required"


def test_preserves_multiple_snapshots_for_same_keyword(tmp_path) -> None:
    """Multiple runs for the same keyword remain separate jobs."""
    settings = _settings(tmp_path)
    repository = SearchRepository(settings)

    repository.create_job(_request("kopi"))
    repository.create_job(_request("kopi"))

    with open_database(settings) as connection:
        job_count = connection.execute("SELECT COUNT(*) FROM search_jobs").fetchone()[0]

    assert job_count == 2
