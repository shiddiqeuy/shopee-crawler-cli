"""Browser management commands."""

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from shopee_cli.browser.exceptions import BrowserConnectionError, BrowserError
from shopee_cli.browser.manager import BrowserManager
from shopee_cli.browser.models import (
    BrowserMode,
    BrowserStatus,
    ConnectionState,
    TabInfo,
)
from shopee_cli.config.settings import get_settings
from shopee_cli.logging.logger import get_logger

browser_app = typer.Typer(help="Manage browser connections and Shopee tabs.")
console = Console()
logger = get_logger(__name__)


@browser_app.command("status")
def show_browser_status() -> None:
    """Show browser connection and Shopee tab status."""
    settings = get_settings()
    manager = BrowserManager(settings=settings)

    try:
        if manager.mode == BrowserMode.MAIN:
            manager.connect()
        status = manager.get_status()
        _print_browser_status(status)
    except BrowserConnectionError as error:
        logger.warning("browser_status_connection_failed", error=str(error))
        _print_browser_status(
            BrowserStatus(
                mode=manager.mode,
                state=ConnectionState.DISCONNECTED,
                message=str(error),
            )
        )
        _print_next_action(manager.mode)
    finally:
        manager.disconnect()


@browser_app.command("connect")
def connect_browser(
    mode: Annotated[
        BrowserMode | None,
        typer.Option(
            "--mode",
            help="Temporarily override the configured browser mode.",
        ),
    ] = None,
) -> None:
    """Connect to the configured browser mode."""
    settings = get_settings()
    manager = BrowserManager(settings=settings, mode=mode)

    try:
        manager.connect()
        if manager.mode == BrowserMode.ISOLATED:
            manager.open_shopee()
        _print_browser_status(manager.get_status())
        if manager.mode == BrowserMode.ISOLATED:
            console.print("Press Ctrl+C or close the browser window to disconnect.")
            manager.wait_until_closed()
    except BrowserConnectionError as error:
        logger.warning(
            "browser_connect_failed",
            mode=manager.mode.value,
            error=str(error),
        )
        _print_connection_error(manager.mode, error)
        raise typer.Exit(1) from error
    finally:
        manager.disconnect()


@browser_app.command("tabs")
def list_browser_tabs(
    include_all: Annotated[
        bool,
        typer.Option(
            "--all",
            help="List all tabs without inspecting non-Shopee pages.",
        ),
    ] = False,
) -> None:
    """List Shopee tabs by default."""
    settings = get_settings()
    manager = BrowserManager(settings=settings)

    try:
        manager.connect()
        tabs = manager.list_tabs(include_all=include_all)
        _print_tabs(tabs)
    except BrowserConnectionError as error:
        logger.warning("browser_tabs_connection_failed", error=str(error))
        _print_connection_error(manager.mode, error)
        raise typer.Exit(1) from error
    finally:
        manager.disconnect()


@browser_app.command("open-shopee")
def open_shopee() -> None:
    """Open or reuse a Shopee marketplace tab."""
    settings = get_settings()
    manager = BrowserManager(settings=settings)

    try:
        manager.connect()
        tab = manager.open_shopee()
        console.print(f"Shopee tab ready: {tab.url}")
        if manager.mode == BrowserMode.ISOLATED:
            console.print("Press Ctrl+C or close the browser window to disconnect.")
            manager.wait_until_closed()
    except BrowserConnectionError as error:
        logger.warning("browser_open_shopee_failed", error=str(error))
        _print_connection_error(manager.mode, error)
        raise typer.Exit(1) from error
    finally:
        manager.disconnect()


@browser_app.command("disconnect")
def disconnect_browser() -> None:
    """Disconnect from the browser without removing profile data."""
    settings = get_settings()
    manager = BrowserManager(settings=settings)
    manager.disconnect()

    if manager.mode == BrowserMode.MAIN:
        console.print(
            "Detached from Main Chrome. User Chrome and tabs were not closed."
        )
        return

    console.print(
        "Closed only the isolated browser context created by this application."
    )


def _print_browser_status(status: BrowserStatus) -> None:
    settings = get_settings()
    table = Table(title="Browser Status")
    table.add_column("Item", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    table.add_row("Browser Mode", status.mode.value)
    table.add_row("Status", status.state.value)
    if status.mode == BrowserMode.MAIN:
        table.add_row("CDP Endpoint", settings.browser_cdp_url)
    else:
        table.add_row("Browser Profile Path", str(settings.browser_profile_path))
    table.add_row("Browser Contexts", str(status.context_count))
    table.add_row("Open Pages", str(status.page_count))
    table.add_row("Shopee Tabs", str(status.shopee_tab_count))
    table.add_row("Shopee Login", status.login_status.value)

    console.print(table)
    if status.message:
        console.print(status.message)


def _print_tabs(tabs: list[TabInfo]) -> None:
    if not tabs:
        console.print("No matching browser tabs found.")
        return

    table = Table(title="Browser Tabs")
    table.add_column("Index", style="cyan", no_wrap=True)
    table.add_column("Title", style="white")
    table.add_column("URL", style="white")
    table.add_column("Active", style="white")
    table.add_column("Login Status", style="white")

    for tab in tabs:
        table.add_row(
            str(tab.index),
            tab.title,
            tab.url,
            "yes" if tab.is_active else "no",
            tab.login_status.value,
        )
    console.print(table)


def _print_connection_error(mode: BrowserMode, error: BrowserError) -> None:
    console.print(str(error))
    if mode == BrowserMode.MAIN:
        console.print(
            "Start Chrome with an approved remote-debugging configuration, then retry:"
        )
        console.print("shopee browser connect --mode main")
        return

    console.print("Check that Playwright browser binaries are installed, then retry.")


def _print_next_action(mode: BrowserMode) -> None:
    if mode == BrowserMode.MAIN:
        console.print(
            "Main Chrome is not available through the configured CDP endpoint."
        )
        return

    console.print("Run shopee browser connect --mode isolated to open the profile.")
