"""Search request validation tests."""

import pytest

from shopee_cli.browser.models import BrowserMode
from shopee_cli.collectors.exceptions import (
    InvalidKeywordError,
    UnsupportedSortModeError,
)
from shopee_cli.collectors.models import SearchSortMode
from shopee_cli.collectors.search_collector import (
    build_search_url,
    create_search_request,
    validate_keyword,
    validate_limit,
    validate_max_scrolls,
)


def test_accepts_valid_keyword() -> None:
    """Valid Indonesian keywords are preserved after trimming."""
    assert validate_keyword("  kopi arabika gayo  ") == "kopi arabika gayo"


def test_rejects_empty_keyword() -> None:
    """Whitespace-only keywords are rejected."""
    with pytest.raises(InvalidKeywordError):
        validate_keyword("   ")


def test_rejects_invalid_limit() -> None:
    """Limits outside the MVP range are rejected."""
    with pytest.raises(ValueError):
        validate_limit(0)
    with pytest.raises(ValueError):
        validate_limit(201)


def test_rejects_invalid_max_scrolls() -> None:
    """Max scrolls outside the MVP range are rejected."""
    with pytest.raises(ValueError):
        validate_max_scrolls(0)
    with pytest.raises(ValueError):
        validate_max_scrolls(31)


def test_rejects_unsupported_sort_mode() -> None:
    """Accepted CLI sort values that are not safely mapped are rejected."""
    with pytest.raises(UnsupportedSortModeError):
        build_search_url("kopi", SearchSortMode.LATEST)


def test_search_url_safely_encodes_keyword() -> None:
    """Search URL uses encoded query parameters."""
    url = build_search_url("kopi arabika", SearchSortMode.RELEVANCE)

    assert url == "https://shopee.co.id/search?keyword=kopi+arabika"


def test_search_url_uses_valid_shopee_domain() -> None:
    """Search request source URL stays on the marketplace domain."""
    request = create_search_request(
        keyword="kopi",
        limit=10,
        browser_mode=BrowserMode.MAIN,
        sort_mode=SearchSortMode.RELEVANCE,
        max_scrolls=3,
    )

    assert request.source_url.startswith("https://shopee.co.id/search?")
