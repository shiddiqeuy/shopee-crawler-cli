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

    def get_search_job(self, job_id: str) -> SearchJob | None:
        """Return a search job by ID."""
        self.initialize_schema()
        try:
            with open_database(self._settings) as connection:
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
            msg = "Search job could not be loaded."
            raise SearchPersistenceError(msg) from error

        return _job_from_row(row) if row else None

    def get_latest_exportable_job(self) -> SearchJob | None:
        """Return the latest completed or partial search job."""
        return self._get_latest_exportable_job_where()

    def get_latest_exportable_job_by_keyword(self, keyword: str) -> SearchJob | None:
        """Return the latest exportable search job for a keyword."""
        return self._get_latest_exportable_job_where(
            "LOWER(keyword) = LOWER(?)", [keyword]
        )

    def get_latest_completed_job(self) -> SearchJob | None:
        """Return the latest completed search job for analytics."""
        return self._get_latest_job_by_status(SearchJobStatus.COMPLETED)

    def get_latest_completed_job_by_keyword(self, keyword: str) -> SearchJob | None:
        """Return the latest completed search job matching a keyword."""
        return self._get_latest_job_by_status(
            SearchJobStatus.COMPLETED,
            "LOWER(keyword) = LOWER(?)",
            [keyword],
        )

    def list_exportable_jobs(self, limit: int = 20) -> list[SearchJob]:
        """List recent completed or partial search jobs."""
        self.initialize_schema()
        try:
            with open_database(self._settings) as connection:
                rows = connection.execute(
                    """
                    SELECT job_id, keyword, requested_limit, collected_count,
                           browser_mode, sort_mode, source_url, status,
                           started_at, finished_at, error_message
                    FROM search_jobs
                    WHERE status IN ('completed', 'partial')
                    ORDER BY COALESCE(finished_at, started_at) DESC, started_at DESC
                    LIMIT ?
                    """,
                    [limit],
                ).fetchall()
        except DuckDBError as error:
            msg = "Exportable search jobs could not be listed."
            raise SearchPersistenceError(msg) from error

        return [_job_from_row(row) for row in rows]

    def get_search_results(self, job_id: str) -> list[SearchResult]:
        """Return stored search results ordered by rank."""
        self.initialize_schema()
        try:
            with open_database(self._settings) as connection:
                rows = connection.execute(
                    """
                    SELECT product_id, rank, product_name, product_url, image_url,
                           price_raw, price_min, price_max, original_price,
                           discount_percentage, sold_raw, sold_count, rating,
                           shop_name, location, is_advertisement, is_mall,
                           is_preferred, collected_at
                    FROM search_results
                    WHERE job_id = ?
                    ORDER BY rank ASC
                    """,
                    [job_id],
                ).fetchall()
        except DuckDBError as error:
            msg = "Search results could not be loaded."
            raise SearchPersistenceError(msg) from error

        return [_result_from_row(row) for row in rows]

    def _get_latest_exportable_job_where(
        self,
        where_clause: str | None = None,
        parameters: list[object] | None = None,
    ) -> SearchJob | None:
        self.initialize_schema()
        status_clause = "status IN ('completed', 'partial')"
        query_parameters = parameters or []
        if where_clause:
            status_clause = f"{status_clause} AND {where_clause}"
        try:
            with open_database(self._settings) as connection:
                row = connection.execute(
                    f"""
                    SELECT job_id, keyword, requested_limit, collected_count,
                           browser_mode, sort_mode, source_url, status,
                           started_at, finished_at, error_message
                    FROM search_jobs
                    WHERE {status_clause}
                    ORDER BY COALESCE(finished_at, started_at) DESC, started_at DESC
                    LIMIT 1
                    """,
                    query_parameters,
                ).fetchone()
        except DuckDBError as error:
            msg = "Exportable search job could not be loaded."
            raise SearchPersistenceError(msg) from error

        return _job_from_row(row) if row else None

    def _get_latest_job_by_status(
        self,
        status: SearchJobStatus,
        where_clause: str | None = None,
        parameters: list[object] | None = None,
    ) -> SearchJob | None:
        self.initialize_schema()
        query_parameters: list[object] = [status.value]
        if parameters:
            query_parameters.extend(parameters)
        extra_clause = f" AND {where_clause}" if where_clause else ""
        try:
            with open_database(self._settings) as connection:
                row = connection.execute(
                    f"""
                    SELECT job_id, keyword, requested_limit, collected_count,
                           browser_mode, sort_mode, source_url, status,
                           started_at, finished_at, error_message
                    FROM search_jobs
                    WHERE status = ?{extra_clause}
                    ORDER BY COALESCE(finished_at, started_at) DESC, started_at DESC
                    LIMIT 1
                    """,
                    query_parameters,
                ).fetchone()
        except DuckDBError as error:
            msg = "Completed search job could not be loaded."
            raise SearchPersistenceError(msg) from error

        return _job_from_row(row) if row else None


def _job_from_row(row: tuple[object, ...]) -> SearchJob:
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


def _result_from_row(row: tuple[object, ...]) -> SearchResult:
    return SearchResult(
        product_id=row[0],
        rank=row[1],
        product_name=row[2],
        product_url=row[3],
        image_url=row[4],
        price_raw=row[5],
        price_min=row[6],
        price_max=row[7],
        original_price=row[8],
        discount_percentage=row[9],
        sold_raw=row[10],
        sold_count=row[11],
        rating=row[12],
        shop_name=row[13],
        location=row[14],
        is_advertisement=row[15],
        is_mall=row[16],
        is_preferred=row[17],
        collected_at=row[18],
    )
