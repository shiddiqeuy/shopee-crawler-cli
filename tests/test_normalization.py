"""Normalization tests."""

from shopee_cli.normalization.price import (
    parse_discount_percentage,
    parse_price_range,
    parse_price_value,
)
from shopee_cli.normalization.sold import parse_rating, parse_sold_count


def test_parse_single_price() -> None:
    """Single displayed prices are parsed as integer Rupiah."""
    assert parse_price_value("Rp25.000") == 25000


def test_parse_price_range() -> None:
    """Displayed price ranges produce min and max values."""
    assert parse_price_range("Rp25.000 - Rp40.000") == (25000, 40000)


def test_parse_indonesian_sold_values() -> None:
    """Compact Indonesian sold values are normalized."""
    assert parse_sold_count("1,2RB") == 1200
    assert parse_sold_count("1,2K") == 1200
    assert parse_sold_count("3JT") == 3000000
    assert parse_sold_count("10+") == 10


def test_empty_sold_value() -> None:
    """Empty sold values stay unknown."""
    assert parse_sold_count("") is None


def test_valid_and_invalid_rating() -> None:
    """Ratings are constrained to visible Shopee rating range."""
    assert parse_rating("4.9") == 4.9
    assert parse_rating("6.0") is None
    assert parse_rating("rating unavailable") is None


def test_discount_percentage() -> None:
    """Discount percentages are parsed from raw text."""
    assert parse_discount_percentage("15%") == 15
