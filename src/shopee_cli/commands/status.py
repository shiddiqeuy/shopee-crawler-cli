"""Status command."""

from rich.console import Console
from rich.table import Table

from shopee_cli import __author__, __version__
from shopee_cli.config.settings import get_settings
from shopee_cli.database.connection import initialize_database


def show_status() -> None:
    """Show local application configuration status."""
    settings = get_settings()
    initialize_database(settings)
    console = Console()

    table = Table(title="Shopee Market Research CLI Status")
    table.add_column("Item", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    table.add_row("Application Version", __version__)
    table.add_row("Author", __author__)
    table.add_row("Database Path", str(settings.database_path))
    table.add_row("Browser Profile Path", str(settings.browser_profile_path))
    table.add_row("Export Folder", str(settings.export_path))
    table.add_row("Environment", settings.environment)

    console.print(table)
