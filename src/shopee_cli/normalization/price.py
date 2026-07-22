"""Price normalization helpers."""

import re

from shopee_cli.normalization.text import clean_text


def parse_price_value(value: str | None) -> int | None:
    """Parse an Indonesian Rupiah price into an integer amount."""
    cleaned = clean_text(value)
    if not cleaned:
        return None

    digits = re.sub(r"[^0-9]", "", cleaned)
    return int(digits) if digits else None


def parse_price_range(value: str | None) -> tuple[int | None, int | None]:
    """Parse a visible Shopee price or price range."""
    cleaned = clean_text(value)
    if not cleaned:
        return None, None

    parts = re.split(r"\s*-\s*", cleaned, maxsplit=1)
    price_min = parse_price_value(parts[0])
    price_max = parse_price_value(parts[1]) if len(parts) > 1 else price_min
    return price_min, price_max


def parse_discount_percentage(value: str | None) -> int | None:
    """Parse a discount percentage from raw text."""
    cleaned = clean_text(value)
    if not cleaned:
        return None

    match = re.search(r"(\d{1,3})\s*%", cleaned)
    return int(match.group(1)) if match else None
