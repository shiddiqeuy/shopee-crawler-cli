"""Sold-count normalization helpers."""

import re
from decimal import Decimal, InvalidOperation

from shopee_cli.normalization.text import clean_text

MULTIPLIERS = {
    "RB": Decimal("1000"),
    "K": Decimal("1000"),
    "JT": Decimal("1000000"),
    "M": Decimal("1000000"),
}


def parse_sold_count(value: str | None) -> int | None:
    """Parse Indonesian compact sold counts into integers."""
    cleaned = clean_text(value)
    if not cleaned:
        return None

    text = cleaned.upper().replace("TERJUAL", "").strip()
    text = text.rstrip("+").strip()
    match = re.search(r"(\d+(?:[,.]\d+)?)\s*([A-Z]+)?", text)
    if not match:
        return None

    number_text = match.group(1).replace(".", "").replace(",", ".")
    suffix = match.group(2) or ""
    try:
        number = Decimal(number_text)
    except InvalidOperation:
        return None

    multiplier = MULTIPLIERS.get(suffix, Decimal("1"))
    return int(number * multiplier)


def parse_rating(value: str | None) -> float | None:
    """Parse a visible rating value."""
    cleaned = clean_text(value)
    if not cleaned:
        return None

    match = re.search(r"(\d+(?:[,.]\d+)?)", cleaned)
    if not match:
        return None

    rating = float(match.group(1).replace(",", "."))
    if rating < 0 or rating > 5:
        return None
    return rating
