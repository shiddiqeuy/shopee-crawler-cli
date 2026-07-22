"""Shopee page safety helpers."""

from urllib.parse import urlparse

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page

from shopee_cli.browser.models import LoginStatus

SHOPEE_HOST = "shopee.co.id"
SHOPEE_HOME_URL = "https://shopee.co.id/"

LOGGED_IN_SELECTORS = (
    "a[href*='/user/account/profile']",
    "a[href*='/buyer/login'] + *",
    "button:has-text('Logout')",
)
LOGGED_OUT_SELECTORS = (
    "a[href*='/buyer/login']",
    "button:has-text('Log In')",
    "button:has-text('Login')",
    "text=Masuk",
)
VERIFICATION_SELECTORS = (
    "text=CAPTCHA",
    "text=Verifikasi",
    "text=Verification",
)


def is_shopee_url(url: str) -> bool:
    """Return whether a URL belongs to shopee.co.id or its subdomains."""
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or ""
    return hostname == SHOPEE_HOST or hostname.endswith(f".{SHOPEE_HOST}")


def is_marketplace_url(url: str) -> bool:
    """Return whether a URL is a regular Shopee marketplace page."""
    parsed_url = urlparse(url)
    return parsed_url.hostname == SHOPEE_HOST


def detect_login_status(page: Page) -> LoginStatus:
    """Best-effort page-level Shopee login status detection."""
    if not is_shopee_url(page.url):
        return LoginStatus.UNKNOWN

    try:
        for selector in VERIFICATION_SELECTORS:
            if page.locator(selector).first.count() > 0:
                return LoginStatus.UNKNOWN
        for selector in LOGGED_IN_SELECTORS:
            if page.locator(selector).first.count() > 0:
                return LoginStatus.LOGGED_IN
        for selector in LOGGED_OUT_SELECTORS:
            if page.locator(selector).first.count() > 0:
                return LoginStatus.LOGGED_OUT
    except PlaywrightError:
        return LoginStatus.UNKNOWN

    return LoginStatus.UNKNOWN
