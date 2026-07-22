"""Browser manager facade."""

from typing import Protocol

from shopee_cli.browser.exceptions import InvalidBrowserModeError
from shopee_cli.browser.isolated import IsolatedBrowser
from shopee_cli.browser.main_chrome import MainChromeBrowser
from shopee_cli.browser.models import BrowserMode, BrowserStatus, TabInfo
from shopee_cli.browser.shopee import SHOPEE_HOME_URL
from shopee_cli.config.settings import Settings, get_settings


class BrowserImplementation(Protocol):
    """Browser implementation protocol."""

    def connect(self) -> None: ...

    def disconnect(self) -> None: ...

    def get_status(self) -> BrowserStatus: ...

    def list_tabs(self, include_all: bool = False) -> list[TabInfo]: ...

    def open_shopee(self, url: str) -> TabInfo: ...


class BrowserManager:
    """Select and operate the configured browser mode."""

    def __init__(
        self,
        settings: Settings | None = None,
        mode: BrowserMode | str | None = None,
    ) -> None:
        base_settings = settings or get_settings()
        try:
            self._mode = (
                BrowserMode(mode) if mode is not None else base_settings.browser_mode
            )
        except ValueError as error:
            msg = f"Unsupported browser mode: {mode}"
            raise InvalidBrowserModeError(msg) from error
        self._settings = base_settings.model_copy(update={"browser_mode": self._mode})
        self._browser = self._create_browser()

    @property
    def mode(self) -> BrowserMode:
        """Return the active browser mode."""
        return self._mode

    def connect(self) -> None:
        """Connect to the active browser mode."""
        self._browser.connect()

    def disconnect(self) -> None:
        """Disconnect from the active browser mode."""
        self._browser.disconnect()

    def get_status(self) -> BrowserStatus:
        """Return browser status."""
        return self._browser.get_status()

    def list_tabs(self, include_all: bool = False) -> list[TabInfo]:
        """List browser tabs."""
        return self._browser.list_tabs(include_all=include_all)

    def open_shopee(self) -> TabInfo:
        """Open or reuse a Shopee marketplace tab."""
        return self._browser.open_shopee(SHOPEE_HOME_URL)

    def wait_until_closed(self) -> None:
        """Keep isolated browser sessions visible until closed by the user."""
        wait = getattr(self._browser, "wait_until_closed", None)
        if wait is not None:
            wait()

    def _create_browser(self) -> BrowserImplementation:
        if self._mode == BrowserMode.MAIN:
            return MainChromeBrowser(self._settings)
        if self._mode == BrowserMode.ISOLATED:
            return IsolatedBrowser(self._settings)

        msg = f"Unsupported browser mode: {self._mode}"
        raise InvalidBrowserModeError(msg)
