"""Excel export orchestration."""

from datetime import UTC, datetime
from pathlib import Path

from openpyxl.utils.exceptions import InvalidFileException

from shopee_cli.collectors.models import SearchJob, SearchJobStatus
from shopee_cli.config.settings import Settings, get_settings
from shopee_cli.database.search_repository import SearchRepository
from shopee_cli.exports.exceptions import (
    ExportDataNotFoundError,
    ExportJobNotFoundError,
    ExportJobNotReadyError,
    WorkbookSaveError,
)
from shopee_cli.exports.filenames import build_default_output_path, validate_output_path
from shopee_cli.exports.models import ExportResult, ExportSelection
from shopee_cli.exports.workbook_builder import build_workbook
from shopee_cli.logging.logger import get_logger

EXPORTABLE_STATUSES = {SearchJobStatus.COMPLETED, SearchJobStatus.PARTIAL}
logger = get_logger(__name__)


class ExcelExporter:
    """Export stored search snapshots to Excel workbooks."""

    def __init__(
        self,
        repository: SearchRepository | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._repository = repository or SearchRepository(self._settings)

    def export(
        self,
        job_id: str | None = None,
        keyword: str | None = None,
        output_path: Path | None = None,
    ) -> ExportResult:
        """Export a selected search snapshot to an Excel workbook."""
        selection = self.select_export_data(job_id=job_id, keyword=keyword)
        path = self._resolve_output_path(selection.job, output_path)
        workbook = build_workbook(selection.job, selection.results, datetime.now(UTC))
        try:
            workbook.save(path)
        except (OSError, InvalidFileException) as error:
            logger.error("excel_workbook_save_failed", path=str(path), error=str(error))
            msg = f"Excel workbook could not be saved: {path}"
            raise WorkbookSaveError(msg) from error
        return ExportResult(
            job=selection.job,
            output_path=path,
            sheet_count=len(workbook.worksheets),
            product_count=len(selection.results),
        )

    def select_export_data(
        self,
        job_id: str | None = None,
        keyword: str | None = None,
    ) -> ExportSelection:
        """Select exportable job and load ordered results."""
        if job_id and keyword:
            msg = "Use either --job-id or --keyword, not both."
            raise ExportJobNotFoundError(msg)

        job = self._select_job(job_id=job_id, keyword=keyword)
        if job.status not in EXPORTABLE_STATUSES:
            msg = (
                f'Search job {job.job_id} has status "{job.status.value}" '
                "and cannot be exported."
            )
            raise ExportJobNotReadyError(msg)

        results = self._repository.get_search_results(job.job_id)
        if job.collected_count > 0 and not results:
            msg = (
                f"Search job {job.job_id} reports {job.collected_count} products, "
                "but no result rows were found."
            )
            raise ExportDataNotFoundError(msg)
        return ExportSelection(job=job, results=results)

    def _select_job(self, job_id: str | None, keyword: str | None) -> SearchJob:
        if job_id:
            job = self._repository.get_search_job(job_id)
            if job is None:
                msg = f"Search job {job_id} was not found."
                raise ExportJobNotFoundError(msg)
            return job
        if keyword:
            job = self._repository.get_latest_exportable_job_by_keyword(keyword.strip())
            if job is None:
                msg = f'No completed or partial search job was found for "{keyword}".'
                raise ExportJobNotFoundError(msg)
            return job

        job = self._repository.get_latest_exportable_job()
        if job is None:
            msg = "No completed or partial search job was found."
            raise ExportJobNotFoundError(msg)
        return job

    def _resolve_output_path(self, job: SearchJob, output_path: Path | None) -> Path:
        if output_path is not None:
            return validate_output_path(output_path)
        return build_default_output_path(
            self._settings.export_path, job.keyword, datetime.now()
        )
