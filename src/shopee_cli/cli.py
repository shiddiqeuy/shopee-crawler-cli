"""Root CLI application."""

import typer

from shopee_cli.commands.browser import browser_app
from shopee_cli.commands.export import export_app
from shopee_cli.commands.search import run_search
from shopee_cli.commands.status import show_status
from shopee_cli.commands.version import show_version
from shopee_cli.logging.logger import configure_logging

app = typer.Typer(
    name="shopee",
    help="Shopee Market Research CLI.",
    no_args_is_help=True,
)

app.command("version")(show_version)
app.command("status")(show_status)
app.command("search")(run_search)
app.add_typer(browser_app, name="browser")
app.add_typer(export_app, name="export")


def main() -> None:
    """Run the Shopee CLI."""
    configure_logging()
    app()
