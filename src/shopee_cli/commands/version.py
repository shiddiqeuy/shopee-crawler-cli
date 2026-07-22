"""Version command."""

from rich.console import Console

from shopee_cli import __version__


def show_version() -> None:
    """Show the application version."""
    console = Console()
    console.print(f"Shopee Market Research CLI {__version__}")
