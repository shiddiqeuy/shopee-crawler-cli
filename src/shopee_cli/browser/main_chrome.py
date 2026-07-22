"""Main Chrome CDP connection implementation."""

from playwright.sync_api import Browser, Error, Playwright, sync_playwright

from shopee_cli.browser.exceptions import BrowserNotAvailableError
from shopee_cli.browser.models import (
    BrowserStatus,
    ConnectionState,
    LoginStatus,
    TabInfo,
)
from shopee_cli.browser.shopee import (
    detect_login_status,
    is_marketplace_url,
    is_shopee_url,
)
from shopee_cli.config.settings import Settings


class MainChromeBrowser:
    """Attach-only connection to a user-controlled Chrome instance."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    def connect(self) -> None:
        """Connect to Chrome through CDP without launching a browser."""
        self._playwright = sync_playwright().start()
        try:
            self._browser = self._playwright.chromium.connect_over_cdp(
                self._settings.browser_cdp_url,
                timeout=self._settings.browser_timeout_ms,
            )
        except (Error, OSError) as error:
            self.disconnect()
            msg = (
                f"Could not connect to Main Chrome at {self._settings.browser_cdp_url}."
            )
            raise BrowserNotAvailableError(msg) from error

    def disconnect(self) -> None:
        """Detach from Chrome without closing the user's browser or tabs."""
        self._browser = None
        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None

    def get_status(self) -> BrowserStatus:
        """Return current attached browser status."""
        if self._browser is None:
            return BrowserStatus(
                mode=self._settings.browser_mode,
                state=ConnectionState.DISCONNECTED,
            )

        tabs = self.list_tabs()
        login_status = next(
            (
                tab.login_status
                for tab in tabs
                if tab.login_status != LoginStatus.UNKNOWN
            ),
            LoginStatus.UNKNOWN,
        )
        return BrowserStatus(
            mode=self._settings.browser_mode,
            state=ConnectionState.CONNECTED,
            context_count=len(self._browser.contexts),
            page_count=sum(len(context.pages) for context in self._browser.contexts),
            shopee_tab_count=sum(tab.is_shopee for tab in tabs),
            login_status=login_status,
        )

    def list_tabs(self, include_all: bool = False) -> list[TabInfo]:
        """List safe tab metadata."""
        if self._browser is None:
            return []

        tabs: list[TabInfo] = []
        tab_index = 0
        for context in self._browser.contexts:
            active_page = context.pages[-1] if context.pages else None
            for page in context.pages:
                is_shopee = is_shopee_url(page.url)
                if not include_all and not is_shopee:
                    continue
                title = page.title() if is_shopee else ""
                login_status = (
                    detect_login_status(page) if is_shopee else LoginStatus.UNKNOWN
                )
                tabs.append(
                    TabInfo(
                        index=tab_index,
                        title=title,
                        url=page.url,
                        is_active=page == active_page,
                        is_shopee=is_shopee,
                        login_status=login_status,
                    )
                )
                tab_index += 1
        return tabs

    def open_shopee(self, url: str) -> TabInfo:
        """Reuse an existing Shopee tab or open Shopee in the attached browser."""
        if self._browser is None:
            self.connect()

        assert self._browser is not None
        tabs = self.list_tabs()
        marketplace_tabs = [tab for tab in tabs if is_marketplace_url(tab.url)]
        if marketplace_tabs:
            return marketplace_tabs[0]

        context = self._browser.contexts[0] if self._browser.contexts else None
        if context is None:
            context = self._browser.new_context()
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded")
        except Error as error:
            msg = "Could not open Shopee in Main Chrome."
            raise BrowserNotAvailableError(msg) from error
        return TabInfo(
            index=0,
            title=page.title(),
            url=page.url,
            is_active=True,
            is_shopee=is_shopee_url(page.url),
            login_status=detect_login_status(page),
        )
