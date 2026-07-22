"""Excel export filename helpers."""

import re
import unicodedata
from datetime import datetime
from pathlib import Path

from shopee_cli.exports.exceptions import ExportFileExistsError, InvalidOutputPathError

MAX_SLUG_LENGTH = 60
INVALID_FILENAME_CHARS = r'<>:"/\\|?*'


def slugify_keyword(keyword: str) -> str:
    """Create a filesystem-safe keyword slug."""
    normalized = unicodedata.normalize("NFKD", keyword.strip().lower())
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(f"[{re.escape(INVALID_FILENAME_CHARS)}]", " ", ascii_text)
    cleaned = re.sub(r"[^a-z0-9]+", "-", cleaned).strip("-")
    return (cleaned or "shopee-search")[:MAX_SLUG_LENGTH].strip("-")


def build_default_output_path(
    export_dir: Path,
    keyword: str,
    timestamp: datetime,
) -> Path:
    """Build a non-overwriting default workbook path."""
    export_dir.mkdir(parents=True, exist_ok=True)
    suffix = timestamp.strftime("%Y%m%d-%H%M%S")
    base_name = f"{slugify_keyword(keyword)}-{suffix}"
    candidate = export_dir / f"{base_name}.xlsx"
    counter = 2
    while candidate.exists():
        candidate = export_dir / f"{base_name}-{counter}.xlsx"
        counter += 1
    return candidate


def validate_output_path(output_path: Path) -> Path:
    """Validate explicit output path without overwriting existing files."""
    if output_path.suffix.lower() != ".xlsx":
        msg = "Excel export output path must end with .xlsx."
        raise InvalidOutputPathError(msg)
    if output_path.exists() and output_path.is_dir():
        msg = "Excel export output path must be a file, not a directory."
        raise InvalidOutputPathError(msg)
    if output_path.exists():
        msg = f"The output file already exists: {output_path}"
        raise ExportFileExistsError(msg)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path
