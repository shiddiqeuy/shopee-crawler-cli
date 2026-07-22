"""Shopee safety helper tests."""

from shopee_cli.browser.models import LoginStatus
from shopee_cli.browser.shopee import (
    detect_login_status,
    is_marketplace_url,
    is_shopee_url,
)


class FakeLocator:
    """Minimal Playwright locator fake."""

    def __init__(self, count: int) -> None:
        self._count = count
        self.first = self

    def count(self) -> int:
        """Return configured selector match count."""
        return self._count


class FakePage:
    """Minimal Playwright page fake."""

    def __init__(self, url: str, matches: set[str] | None = None) -> None:
        self.url = url
        self._matches = matches or set()

    def locator(self, selector: str) -> FakeLocator:
        """Return a fake locator for selector matching."""
        return FakeLocator(1 if selector in self._matches else 0)


def test_shopee_hostname_validation_accepts_valid_domains() -> None:
    """Shopee host and subdomains are valid."""
    assert is_shopee_url("https://shopee.co.id/")
    assert is_shopee_url("https://seller.shopee.co.id/")


def test_shopee_hostname_validation_rejects_deceptive_domains() -> None:
    """URLs that merely contain Shopee text are rejected."""
    assert not is_shopee_url("https://example.com/?url=shopee.co.id")
    assert not is_shopee_url("https://fake-shopee.co.id/")


def test_marketplace_validation_prefers_regular_shopee_pages() -> None:
    """Marketplace validation excludes Seller Center subdomains."""
    assert is_marketplace_url("https://shopee.co.id/")
    assert not is_marketplace_url("https://seller.shopee.co.id/")


def test_login_status_supports_logged_in() -> None:
    """Login status can report logged_in."""
    page = FakePage(
        "https://shopee.co.id/",
        {"a[href*='/user/account/profile']"},
    )
    assert detect_login_status(page) == LoginStatus.LOGGED_IN


def test_login_status_supports_logged_out() -> None:
    """Login status can report logged_out."""
    page = FakePage("https://shopee.co.id/", {"a[href*='/buyer/login']"})
    assert detect_login_status(page) == LoginStatus.LOGGED_OUT


def test_login_status_supports_unknown() -> None:
    """Login status can report unknown."""
    page = FakePage("https://shopee.co.id/")
    assert detect_login_status(page) == LoginStatus.UNKNOWN
