"""Product card parser and deduplication tests."""

from datetime import UTC, datetime

from shopee_cli.collectors.models import SearchResult
from shopee_cli.collectors.parser import deduplicate_results, parse_product_card


class FakeLocator:
    """Minimal locator fake."""

    def __init__(self, items: list[object]) -> None:
        self._items = items
        self.first = items[0] if items else self

    def count(self) -> int:
        """Return item count."""
        return len(self._items)


class FakeNode:
    """Minimal product card node fake."""

    def __init__(
        self,
        text: str,
        href: str,
        attributes: dict[str, str] | None = None,
        selectors: dict[str, list[object]] | None = None,
    ) -> None:
        self._text = text
        self._href = href
        self._attributes = attributes or {}
        self._selectors = selectors or {}

    def inner_text(self) -> str:
        """Return visible text."""
        return self._text

    def get_attribute(self, name: str) -> str | None:
        """Return fake attributes."""
        if name == "href":
            return self._href
        return self._attributes.get(name)

    def locator(self, selector: str) -> FakeLocator:
        """Return matching fake child nodes."""
        return FakeLocator(self._selectors.get(selector, []))


def test_parses_complete_product_card() -> None:
    """Parser extracts visible raw and normalized fields."""
    image = FakeNode("", "", {"src": "https://img.example/item.jpg"})
    card = FakeNode(
        "Kopi Arabika\nRp25.000\n1,2RB terjual\n4.9\nJakarta",
        "https://shopee.co.id/Kopi-i.123.456?sp_atk=x",
        selectors={"img": [image], "text=/^Iklan$/i": [FakeNode("Iklan", "")]},
    )

    result = parse_product_card(card, 1, datetime.now(UTC))

    assert result is not None
    assert result.product_id == "456"
    assert result.product_name == "Kopi Arabika"
    assert result.price_raw == "Rp25.000"
    assert result.price_min == 25000
    assert result.sold_count == 1200
    assert result.is_advertisement is True


def test_parses_product_card_with_missing_optional_fields() -> None:
    """Missing optional values remain null instead of invented."""
    card = FakeNode("Kopi Robusta\nRp30.000", "https://shopee.co.id/Kopi-i.123.789")

    result = parse_product_card(card, 1, datetime.now(UTC))

    assert result is not None
    assert result.product_name == "Kopi Robusta"
    assert result.original_price is None
    assert result.shop_name is None
    assert result.is_advertisement is None


def test_deduplicates_identical_product_ids() -> None:
    """Product ID is the preferred dedupe identity."""
    now = datetime.now(UTC)
    results = [
        SearchResult(
            product_id="1",
            rank=1,
            product_name="A",
            product_url="https://shopee.co.id/A-i.1.1",
            collected_at=now,
        ),
        SearchResult(
            product_id="1",
            rank=2,
            product_name="A duplicate",
            product_url="https://shopee.co.id/A-i.1.1?x=1",
            collected_at=now,
        ),
    ]

    assert len(deduplicate_results(results)) == 1


def test_deduplicates_canonical_urls() -> None:
    """Canonical URL is used when product ID is unavailable."""
    now = datetime.now(UTC)
    results = [
        SearchResult(
            rank=1,
            product_name="A",
            product_url="https://shopee.co.id/a?x=1",
            collected_at=now,
        ),
        SearchResult(
            rank=2,
            product_name="A",
            product_url="https://shopee.co.id/a?x=2",
            collected_at=now,
        ),
    ]

    assert len(deduplicate_results(results)) == 1


def test_preserves_different_products() -> None:
    """Different product identities are preserved."""
    now = datetime.now(UTC)
    results = [
        SearchResult(
            product_id="1",
            rank=1,
            product_name="A",
            product_url="https://shopee.co.id/A-i.1.1",
            collected_at=now,
        ),
        SearchResult(
            product_id="2",
            rank=2,
            product_name="B",
            product_url="https://shopee.co.id/B-i.1.2",
            collected_at=now,
        ),
    ]

    assert len(deduplicate_results(results)) == 2
