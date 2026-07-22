"""Export filename tests."""

from datetime import datetime

import pytest

from shopee_cli.exports.exceptions import ExportFileExistsError, InvalidOutputPathError
from shopee_cli.exports.filenames import (
    build_default_output_path,
    slugify_keyword,
    validate_output_path,
)


def test_creates_safe_slug_and_handles_spaces() -> None:
    """Keyword slugs are filesystem-safe."""
    assert slugify_keyword("Kopi Arabika Gayo") == "kopi-arabika-gayo"


def test_handles_indonesian_characters() -> None:
    """Indonesian characters are normalized safely."""
    assert slugify_keyword("kopi susu gula aren") == "kopi-susu-gula-aren"


def test_removes_invalid_filename_characters() -> None:
    """Invalid filename characters are removed."""
    assert slugify_keyword('kopi:arabika/"gayo"') == "kopi-arabika-gayo"


def test_adds_timestamp_to_default_filename(tmp_path) -> None:
    """Default filenames include keyword slug and timestamp."""
    path = build_default_output_path(
        tmp_path,
        "kopi arabika",
        datetime(2026, 7, 22, 15, 30, 0),
    )

    assert path.name == "kopi-arabika-20260722-153000.xlsx"


def test_prevents_silent_overwrite_with_collision_suffix(tmp_path) -> None:
    """Default filenames add suffixes on collision."""
    existing = tmp_path / "kopi-20260722-153000.xlsx"
    existing.write_text("exists")

    path = build_default_output_path(tmp_path, "kopi", datetime(2026, 7, 22, 15, 30))

    assert path.name == "kopi-20260722-153000-2.xlsx"


def test_rejects_existing_explicit_output(tmp_path) -> None:
    """Explicit output paths are not overwritten."""
    existing = tmp_path / "report.xlsx"
    existing.write_text("exists")

    with pytest.raises(ExportFileExistsError):
        validate_output_path(existing)


def test_rejects_non_xlsx_output(tmp_path) -> None:
    """Only .xlsx outputs are accepted."""
    with pytest.raises(InvalidOutputPathError):
        validate_output_path(tmp_path / "report.csv")
