"""Export domain exceptions."""


class ExportError(Exception):
    """Base export error."""


class ExportJobNotFoundError(ExportError):
    """Raised when an exportable job cannot be found."""


class ExportJobNotReadyError(ExportError):
    """Raised when a job status cannot be exported."""


class ExportDataNotFoundError(ExportError):
    """Raised when job metadata and result rows are inconsistent."""


class InvalidOutputPathError(ExportError):
    """Raised when an output path is invalid."""


class ExportFileExistsError(ExportError):
    """Raised when an output file would be overwritten."""


class WorkbookBuildError(ExportError):
    """Raised when workbook creation fails."""


class WorkbookSaveError(ExportError):
    """Raised when workbook saving fails."""


class ExportOpenError(ExportError):
    """Raised when a generated workbook cannot be opened automatically."""
