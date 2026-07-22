"""Interactive menu tests."""

from typer.testing import CliRunner

from shopee_cli.cli import app

runner = CliRunner()


def test_menu_help_appears() -> None:
    """Menu command help is available from the root CLI."""
    result = runner.invoke(app, ["menu", "--help"])

    assert result.exit_code == 0
    assert "--once" in result.output


def test_menu_exit_option(monkeypatch) -> None:
    """Menu command exits when option 8 is chosen."""
    monkeypatch.setattr(
        "shopee_cli.commands.status.initialize_database",
        lambda settings: None,
    )
    result = runner.invoke(app, ["menu", "--once"], input="8\n")

    assert result.exit_code == 0
    assert "Shopee Market Research CLI" in result.output
    assert "Terima kasih" in result.output
