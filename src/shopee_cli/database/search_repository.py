"""DuckDB persistence for search snapshots."""

from datetime import UTC, datetime
from uuid import uuid4

from duckdb import Error as DuckDBError

from shopee_cli.collectors.exceptions import SearchPersistenceError
from shopee_cli.collectors.models import (
    SearchCollection,
    SearchJob,
    SearchJobStatus,
    SearchRequest,
    SearchResult,
)
from shopee_cli.config.settings import Settings, get_settings
from shopee_cli.database.connection import open_database
from shopee_cli.database.migrations import initialize_search_schema


class SearchRepository:
    """Persist search jobs and results as historical snapshots."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def initialize_schema(self) -> None:
        """Create schema idempotently."""
        try:
            with open_database(self._settings) as connection:
                initialize_search_schema(connection)
        except DuckDBError as error:
            msg = "Search database schema could not be initialized."
            raise SearchPersistenceError(msg) from error

    def create_job(self, request: SearchRequest) -> SearchJob:
        """Create a running search job."""
        self.initialize_schema()
        job = SearchJob(
            job_id=f"srch_{uuid4().hex}",
            keyword=request.keyword,
            requested_limit=request.requested_limit,
            collected_count=0,
            browser_mode=request.browser_mode,
            sort_mode=request.sort_mode,
            source_url=request.source_url,
            status=SearchJobStatus.RUNNING,
            started_at=datetime.now(UTC),
        )
        try:
            with open_database(self._settings) as connection:
                connection.execute(
                    """
                    INSERT INTO search_jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        job.job_id,
                        job.keyword,
                        job.requested_limit,
                        job.collected_count,
                        job.browser_mode.value,
                        job.sort_mode.value,
                        job.source_url,
                        job.status.value,
                        job.started_at,
                        job.finished_at,
                        job.error_message,
                    ],
                )
        except DuckDBError as error:
            msg = "Search job could not be created."
            raise SearchPersistenceError(msg) from error
        return job

    def save_results(self, job_id: str, results: list[SearchResult]) -> None:
        """Save collected search results."""
        try:
            with open_database(self._settings) as connection:
                for result in results:
                    connection.execute(
                        """
                        INSERT INTO search_results VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                            ?
                        )
                        """,
                        [
                            f"res_{uuid4().hex}",
                            job_id,
                            result.product_id,
                            result.rank,
                            result.product_name,
                            result.product_url,
                            result.image_url,
                            result.price_raw,
                            result.price_min,
                            result.price_max,
                            result.original_price,
                            result.discount_percentage,
                            result.sold_raw,
                            result.sold_count,
                            result.rating,
                            result.shop_name,
                            result.location,
                            result.is_advertisement,
                            result.is_mall,
                            result.is_preferred,
                            result.collected_at,
                        ],
                    )
        except DuckDBError as error:
            msg = "Search results could not be saved."
            raise SearchPersistenceError(msg) from error

    def complete_job(self, job_id: str, collection: SearchCollection) -> SearchJob:
        """Persist results and mark a job completed."""
        self.save_results(job_id, collection.results)
        return self.update_job_status(
            job_id=job_id,
            status=collection.status,
            collected_count=len(collection.results),
            error_message=collection.error_message,
        )

    def update_job_status(
        self,
        job_id: str,
        status: SearchJobStatus,
        collected_count: int = 0,
        error_message: str | None = None,
    ) -> SearchJob:
        """Update job status and return current metadata."""
        finished_at = datetime.now(UTC)
        try:
            with open_database(self._settings) as connection:
                connection.execute(
                    """
                    UPDATE search_jobs
                    SET status = ?, collected_count = ?, finished_at = ?,
                        error_message = ?
                    WHERE job_id = ?
                    """,
                    [status.value, collected_count, finished_at, error_message, job_id],
                )
                row = connection.execute(
                    """
                    SELECT job_id, keyword, requested_limit, collected_count,
                           browser_mode, sort_mode, source_url, status,
                           started_at, finished_at, error_message
                    FROM search_jobs
                    WHERE job_id = ?
                    """,
                    [job_id],
                ).fetchone()
        except DuckDBError as error:
            msg = "Search job status could not be updated."
            raise SearchPersistenceError(msg) from error

        return SearchJob(
            job_id=row[0],
            keyword=row[1],
            requested_limit=row[2],
            collected_count=row[3],
            browser_mode=row[4],
            sort_mode=row[5],
            source_url=row[6],
            status=row[7],
            started_at=row[8],
            finished_at=row[9],
            error_message=row[10],
        )
