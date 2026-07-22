"""Analytics statistics tests."""

from shopee_cli.analytics.statistics import (
    average,
    median,
    percentage,
    quartiles,
    unique_count,
)


def test_median_odd_and_even_values() -> None:
    """Median is deterministic for odd and even row counts."""
    assert median([3, 1, 2]) == 2
    assert median([1, 3]) == 2


def test_average_ignores_missing_values() -> None:
    """Average ignores null values."""
    assert average([10, None, 20]) == 15


def test_quartiles_are_deterministic() -> None:
    """Quartiles use median-of-halves."""
    assert quartiles([1, 2, 3, 4, 5]) == (1.5, 3.0, 4.5)


def test_percentage_handles_zero_total() -> None:
    """Percentage does not divide by zero."""
    assert percentage(1, 4) == 25
    assert percentage(1, 0) is None


def test_unique_count_ignores_empty_values() -> None:
    """Unique count trims and ignores empty values."""
    assert unique_count([" A ", "A", "", None, "B"]) == 2
