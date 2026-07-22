"""Browser settings and model tests."""

import pytest
from pydantic import ValidationError

from shopee_cli.browser.exceptions import InvalidBrowserModeError
from shopee_cli.browser.manager import BrowserManager
from shopee_cli.browser.models import BrowserMode
from shopee_cli.config.settings import Settings


def test_validates_allowed_browser_modes() -> None:
    """Settings accept supported browser modes."""
    assert Settings(browser_mode="main").browser_mode == BrowserMode.MAIN
    assert Settings(browser_mode="isolated").browser_mode == BrowserMode.ISOLATED


def test_rejects_invalid_browser_mode() -> None:
    """Settings reject unsupported browser modes."""
    with pytest.raises(ValidationError):
        Settings(browser_mode="unsupported")


def test_manager_rejects_invalid_browser_mode() -> None:
    """Manager raises a domain exception for unsupported overrides."""
    with pytest.raises(InvalidBrowserModeError):
        BrowserManager(settings=Settings(), mode="unsupported")
