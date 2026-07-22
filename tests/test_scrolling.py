"""Scrolling behavior tests."""

from shopee_cli.collectors.scrolling import scroll_until_complete


class FakeMouse:
    """Fake mouse object."""

    def __init__(self) -> None:
        self.scrolls = 0

    def wheel(self, x: int, y: int) -> None:
        """Record scroll calls."""
        self.scrolls += 1


class FakePage:
    """Fake page with mouse and waits."""

    def __init__(self) -> None:
        self.mouse = FakeMouse()

    def wait_for_timeout(self, timeout: int) -> None:
        """No-op wait."""


def test_scrolling_stops_at_requested_limit() -> None:
    """Scrolling stops when enough unique products are available."""
    page = FakePage()
    counts = iter([0, 3, 5])

    scroll_until_complete(page, lambda: next(counts), requested_limit=5, max_scrolls=10)

    assert page.mouse.scrolls == 2


def test_scrolling_stops_at_max_scrolls() -> None:
    """Scrolling honors max scroll count."""
    page = FakePage()
    count = 0

    def growing_count() -> int:
        nonlocal count
        count += 1
        return count

    scroll_until_complete(page, growing_count, requested_limit=10, max_scrolls=3)

    assert page.mouse.scrolls == 3


def test_scrolling_stops_after_repeated_no_growth() -> None:
    """Scrolling stops after two stagnant attempts."""
    page = FakePage()

    scroll_until_complete(page, lambda: 1, requested_limit=10, max_scrolls=10)

    assert page.mouse.scrolls == 2
