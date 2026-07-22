"""Mocked search collector tests."""

import pytest

from shopee_cli.browser.models import BrowserMode
from shopee_cli.collectors.exceptions import SearchVerificationRequiredError
from shopee_cli.collectors.models import SearchJobStatus, SearchSortMode
from shopee_cli.collectors.search_collector import (
    SearchCollector,
    create_search_request,
)


class FakeMouse:
    """Fake mouse."""

    def wheel(self, x: int, y: int) -> None:
        """No-op scroll."""


class FakeLocator:
    """Fake locator collection."""

    def __init__(self, items: list[object]) -> None:
        self._items = items
        self.first = self

    def count(self) -> int:
        """Return count."""
        return len(self._items)

    def nth(self, index: int) -> object:
        """Return nth item."""
        return self._items[index]


class FakeCard:
    """Fake product card."""

    def __init__(self, name: str, href: str) -> None:
        self._name = name
        self._href = href

    def inner_text(self) -> str:
        """Return card text."""
        return f"{self._name}\nRp25.000\n10 terjual"

    def get_attribute(self, name: str) -> str | None:
        """Return card link."""
        return self._href if name == "href" else None

    def locator(self, selector: str) -> FakeLocator:
        """No child selector matches."""
        return FakeLocator([])


class FakePage:
    """Fake Shopee search page."""

    def __init__(self, verification: bool = False) -> None:
        self.mouse = FakeMouse()
        self.url = "https://shopee.co.id/"
        self.verification = verification
        self.cards = [
            FakeCard("Kopi A", "https://shopee.co.id/Kopi-A-i.1.1"),
            FakeCard("Kopi B", "https://shopee.co.id/Kopi-B-i.1.2"),
        ]

    def goto(self, url: str, wait_until: str) -> None:
        """Record navigation."""
        self.url = url

    def wait_for_load_state(self, state: str, timeout: int) -> None:
        """No-op load wait."""

    def wait_for_timeout(self, timeout: int) -> None:
        """No-op scroll wait."""

    def locator(self, selector: str) -> FakeLocator:
        """Return product cards or verification indicator."""
        if selector == "[data-sqe='item']":
            return FakeLocator(self.cards)
        if self.verification and "Verification" in selector:
            return FakeLocator([object()])
        return FakeLocator([])


class FakeManager:
    """Fake BrowserManager."""

    def __init__(self, page: FakePage) -> None:
        self.page = page
        self.requested_page = False

    def get_or_open_shopee_page(self) -> FakePage:
        """Return fake marketplace page."""
        self.requested_page = True
        return self.page


def _request():
    return create_search_request(
        keyword="kopi",
        limit=2,
        browser_mode=BrowserMode.MAIN,
        sort_mode=SearchSortMode.RELEVANCE,
        max_scrolls=1,
    )


def test_mocked_successful_collection() -> None:
    """Collector gathers visible cards through Browser Manager."""
    manager = FakeManager(FakePage())

    collection = SearchCollector(manager).collect(_request())

    assert manager.requested_page
    assert collection.status == SearchJobStatus.COMPLETED
    assert len(collection.results) == 2
    assert collection.results[0].rank == 1


def test_mocked_failed_collection_for_verification() -> None:
    """Verification pages stop automation."""
    manager = FakeManager(FakePage(verification=True))

    with pytest.raises(SearchVerificationRequiredError):
        SearchCollector(manager).collect(_request())
