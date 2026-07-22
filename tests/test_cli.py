"""CLI command tests."""

from typer.testing import CliRunner

from shopee_cli.browser.exceptions import BrowserNotAvailableError
from shopee_cli.browser.models import BrowserMode
from shopee_cli.cli import app

runner = CliRunner()


def test_existing_version_command_still_works() -> None:
    """Milestone 1 version command still works."""
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "Shopee Market Research CLI 0.1.0" in result.output


def test_existing_status_command_still_works(monkeypatch) -> None:
    """Milestone 1 status command still works."""
    monkeypatch.setattr(
        "shopee_cli.commands.status.initialize_database",
        lambda settings: None,
    )

    result = runner.invoke(app, ["status"])

    assert result.exit_code == 0
    assert "Application Version" in result.output


def test_browser_help_lists_subcommands() -> None:
    """Browser help exposes milestone commands."""
    result = runner.invoke(app, ["browser", "--help"])

    assert result.exit_code == 0
    assert "status" in result.output
    assert "connect" in result.output
    assert "tabs" in result.output
    assert "open-shopee" in result.output


def test_search_help_appears() -> None:
    """Search command help is available from the root CLI."""
    result = runner.invoke(app, ["search", "--help"])

    assert result.exit_code == 0
    assert "--limit" in result.output
    assert "--max-scrolls" in result.output


def test_export_help_appears() -> None:
    """Export command help is available from the root CLI."""
    result = runner.invoke(app, ["export", "--help"])

    assert result.exit_code == 0
    assert "excel" in result.output
    assert "jobs" in result.output


def test_export_excel_help_appears() -> None:
    """Excel export help exposes selection options."""
    result = runner.invoke(app, ["export", "excel", "--help"])

    assert result.exit_code == 0
    assert "--job-id" in result.output
    assert "--keyword" in result.output


def test_export_jobs_help_appears() -> None:
    """Export jobs help exposes limit option."""
    result = runner.invoke(app, ["export", "jobs", "--help"])

    assert result.exit_code == 0
    assert "--limit" in result.output


def test_analytics_help_appears() -> None:
    """Analytics command help exposes snapshot selectors."""
    result = runner.invoke(app, ["analytics", "--help"])

    assert result.exit_code == 0
    assert "--job-id" in result.output
    assert "--keyword" in result.output


def test_insight_help_appears() -> None:
    """Insight command help exposes provider and output options."""
    result = runner.invoke(app, ["insight", "--help"])

    assert result.exit_code == 0
    assert "--provider" in result.output
    assert "--output" in result.output


def test_connection_errors_produce_actionable_messages(monkeypatch) -> None:
    """Connection failures print concise retry guidance."""

    class FakeManager:
        """BrowserManager fake that cannot connect."""

        mode = BrowserMode.MAIN

        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def connect(self) -> None:
            raise BrowserNotAvailableError(
                "Could not connect to Main Chrome at http://127.0.0.1:9222."
            )

        def disconnect(self) -> None:
            pass

    monkeypatch.setattr("shopee_cli.commands.browser.BrowserManager", FakeManager)

    result = runner.invoke(app, ["browser", "connect", "--mode", "main"])

    assert result.exit_code == 1
    assert "Could not connect to Main Chrome" in result.output
    assert "shopee browser connect --mode main" in result.output
