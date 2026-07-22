"""Root CLI application."""

import typer

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


def main() -> None:
    """Run the Shopee CLI."""
    configure_logging()
    app()
