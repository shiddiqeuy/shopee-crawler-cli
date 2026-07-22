"""Browser implementation tests using fakes."""

from shopee_cli.browser.isolated import IsolatedBrowser
from shopee_cli.browser.main_chrome import MainChromeBrowser
from shopee_cli.browser.models import BrowserMode, LoginStatus
from shopee_cli.config.settings import Settings


class FakePlaywrightRunner:
    """Fake sync_playwright runner."""

    def __init__(self, chromium: object) -> None:
        self.chromium = chromium
        self.stopped = False

    def start(self) -> "FakePlaywrightRunner":
        """Return the started fake runner."""
        return self

    def stop(self) -> None:
        """Record stop calls."""
        self.stopped = True


class FakeRemoteBrowser:
    """Fake user-controlled browser."""

    contexts: list[object] = []

    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        """Record unexpected close calls."""
        self.closed = True


class FakeMainChromium:
    """Fake Chromium API for main mode."""

    def __init__(self, browser: FakeRemoteBrowser) -> None:
        self.browser = browser
        self.connected_url: str | None = None
        self.launch_called = False

    def connect_over_cdp(self, url: str, timeout: int) -> FakeRemoteBrowser:
        """Record CDP connection arguments."""
        self.connected_url = url
        return self.browser

    def launch_persistent_context(self, *args: object, **kwargs: object) -> None:
        """Record forbidden main-mode launch attempts."""
        self.launch_called = True


class FakeIsolatedChromium:
    """Fake Chromium API for isolated mode."""

    def __init__(self) -> None:
        self.user_data_dir: str | None = None
        self.headless: bool | None = None

    def launch_persistent_context(
        self,
        user_data_dir: str,
        headless: bool,
        timeout: int,
    ) -> object:
        """Record persistent context arguments."""
        self.user_data_dir = user_data_dir
        self.headless = headless
        return object()


class FakePage:
    """Fake page for tab listing."""

    def __init__(self, url: str, title: str) -> None:
        self.url = url
        self._title = title

    def title(self) -> str:
        """Return fake page title."""
        return self._title


class FakeContext:
    """Fake browser context."""

    def __init__(self, pages: list[FakePage]) -> None:
        self.pages = pages


def test_main_mode_does_not_launch_browser(monkeypatch) -> None:
    """Main mode attaches through CDP without launching another browser."""
    browser = FakeRemoteBrowser()
    chromium = FakeMainChromium(browser)
    runner = FakePlaywrightRunner(chromium)
    monkeypatch.setattr(
        "shopee_cli.browser.main_chrome.sync_playwright",
        lambda: runner,
    )

    main_browser = MainChromeBrowser(Settings(browser_mode=BrowserMode.MAIN))
    main_browser.connect()

    assert chromium.connected_url == "http://127.0.0.1:9222"
    assert not chromium.launch_called


def test_main_mode_does_not_close_user_browser() -> None:
    """Main disconnect does not close the user-controlled browser."""
    browser = FakeRemoteBrowser()
    main_browser = MainChromeBrowser(Settings(browser_mode=BrowserMode.MAIN))
    main_browser._browser = browser

    main_browser.disconnect()

    assert not browser.closed


def test_isolated_mode_uses_configured_profile_path(tmp_path, monkeypatch) -> None:
    """Isolated mode launches with the configured profile directory."""
    chromium = FakeIsolatedChromium()
    runner = FakePlaywrightRunner(chromium)
    monkeypatch.setattr("shopee_cli.browser.isolated.sync_playwright", lambda: runner)
    profile_path = tmp_path / "browser-profile"

    isolated_browser = IsolatedBrowser(
        Settings(browser_mode=BrowserMode.ISOLATED, browser_profile_path=profile_path)
    )
    isolated_browser.connect()

    assert chromium.user_data_dir == str(profile_path)
    assert profile_path.exists()


def test_tab_listing_filters_non_shopee_pages_by_default(monkeypatch) -> None:
    """Default tab listing returns only Shopee tabs."""
    monkeypatch.setattr(
        "shopee_cli.browser.main_chrome.detect_login_status",
        lambda page: LoginStatus.UNKNOWN,
    )
    shopee_page = FakePage("https://shopee.co.id/product", "Shopee")
    other_page = FakePage("https://example.com/?url=shopee.co.id", "Example")
    main_browser = MainChromeBrowser(Settings(browser_mode=BrowserMode.MAIN))
    main_browser._browser = type(
        "Browser",
        (),
        {"contexts": [FakeContext([other_page, shopee_page])]},
    )()

    tabs = main_browser.list_tabs()

    assert len(tabs) == 1
    assert tabs[0].url == "https://shopee.co.id/product"
