"""Text normalization helpers."""

import re


def clean_text(value: str | None) -> str | None:
    """Normalize whitespace while preserving the user's text meaning."""
    if value is None:
        return None
    cleaned = re.sub(r"\s+", " ", value).strip()
    return cleaned or None
