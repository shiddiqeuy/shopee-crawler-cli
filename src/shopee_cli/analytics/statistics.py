"""Pure deterministic statistics helpers."""

from collections.abc import Iterable


def non_null(values: Iterable[int | float | None]) -> list[int | float]:
    """Return values excluding nulls."""
    return [value for value in values if value is not None]


def count(values: Iterable[object]) -> int:
    """Return item count."""
    return len(list(values))


def average(values: Iterable[int | float | None]) -> float | None:
    """Return arithmetic average ignoring nulls."""
    numbers = non_null(values)
    return sum(numbers) / len(numbers) if numbers else None


def median(values: Iterable[int | float | None]) -> float | None:
    """Return median ignoring nulls."""
    numbers = sorted(non_null(values))
    if not numbers:
        return None
    middle = len(numbers) // 2
    if len(numbers) % 2 == 1:
        return float(numbers[middle])
    return float((numbers[middle - 1] + numbers[middle]) / 2)


def quartiles(
    values: Iterable[int | float | None],
) -> tuple[float | None, float | None, float | None]:
    """Return Q1, median, and Q3 using deterministic median-of-halves."""
    numbers = sorted(non_null(values))
    if not numbers:
        return None, None, None
    middle = len(numbers) // 2
    lower = numbers[:middle]
    upper = numbers[middle + 1 :] if len(numbers) % 2 == 1 else numbers[middle:]
    return median(lower), median(numbers), median(upper)


def percentage(part: int, total: int) -> float | None:
    """Return deterministic percentage."""
    if total == 0:
        return None
    return (part / total) * 100


def unique_count(values: Iterable[str | None]) -> int:
    """Count unique non-empty strings after trimming whitespace."""
    return len({value.strip() for value in values if value and value.strip()})
