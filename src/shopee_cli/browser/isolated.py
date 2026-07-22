"""Isolated persistent browser profile implementation."""

from playwright.sync_api import (
    BrowserContext,
    Error,
    Page,
    Playwright,
    sync_playwright,
)

from shopee_cli.browser.exceptions import BrowserConnectionError
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


class IsolatedBrowser:
    """Application-owned persistent browser context."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._playwright: Playwright | None = None
        self._context: BrowserContext | None = None

    def connect(self) -> None:
        """Launch a persistent context using the configured profile path."""
        self._settings.browser_profile_path.mkdir(parents=True, exist_ok=True)
        self._playwright = sync_playwright().start()
        try:
            self._context = self._playwright.chromium.launch_persistent_context(
                user_data_dir=str(self._settings.browser_profile_path),
                headless=self._settings.browser_headless,
                timeout=self._settings.browser_timeout_ms,
            )
        except Error as error:
            self.disconnect()
            msg = "Could not launch the isolated browser profile."
            raise BrowserConnectionError(msg) from error

    def disconnect(self) -> None:
        """Close only the context created by this application."""
        if self._context is not None:
            self._context.close()
            self._context = None
        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None

    def get_status(self) -> BrowserStatus:
        """Return current isolated browser status."""
        if self._context is None:
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
            context_count=1,
            page_count=len(self._context.pages),
            shopee_tab_count=sum(tab.is_shopee for tab in tabs),
            login_status=login_status,
        )

    def list_tabs(self, include_all: bool = False) -> list[TabInfo]:
        """List safe tab metadata."""
        if self._context is None:
            return []

        active_page = self._context.pages[-1] if self._context.pages else None
        tabs: list[TabInfo] = []
        for index, page in enumerate(self._context.pages):
            is_shopee = is_shopee_url(page.url)
            if not include_all and not is_shopee:
                continue
            tabs.append(
                TabInfo(
                    index=index,
                    title=page.title() if is_shopee else "",
                    url=page.url,
                    is_active=page == active_page,
                    is_shopee=is_shopee,
                    login_status=detect_login_status(page)
                    if is_shopee
                    else LoginStatus.UNKNOWN,
                )
            )
        return tabs

    def open_shopee(self, url: str) -> TabInfo:
        """Reuse an existing Shopee tab or open Shopee in the isolated profile."""
        page = self.get_or_open_shopee_page(url)
        return TabInfo(
            index=0,
            title=page.title(),
            url=page.url,
            is_active=True,
            is_shopee=is_shopee_url(page.url),
            login_status=detect_login_status(page),
        )

    def get_or_open_shopee_page(self, url: str) -> Page:
        """Return an existing marketplace page or open a new one."""
        if self._context is None:
            self.connect()

        assert self._context is not None
        for page in self._context.pages:
            if is_marketplace_url(page.url):
                return page

        page = self._context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded")
        except Error as error:
            msg = "Could not open Shopee in the isolated browser profile."
            raise BrowserConnectionError(msg) from error
        return page

    def wait_until_closed(self) -> None:
        """Keep the CLI attached while the isolated browser is open."""
        if self._context is None:
            return
        while self._context.pages:
            self._context.pages[0].wait_for_timeout(1000)
