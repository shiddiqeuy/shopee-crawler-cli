"""DuckDB connection handling."""

from collections.abc import Iterator
from contextlib import contextmanager

import duckdb
from duckdb import DuckDBPyConnection

from shopee_cli.config.settings import Settings, get_settings


def initialize_database(settings: Settings | None = None) -> None:
    """Create or open the DuckDB database file without creating tables."""
    active_settings = settings or get_settings()
    active_settings.database_dir.mkdir(parents=True, exist_ok=True)

    connection = duckdb.connect(str(active_settings.database_path))
    connection.close()


@contextmanager
def open_database(settings: Settings | None = None) -> Iterator[DuckDBPyConnection]:
    """Open a DuckDB connection for callers that need direct access."""
    active_settings = settings or get_settings()
    active_settings.database_dir.mkdir(parents=True, exist_ok=True)

    connection = duckdb.connect(str(active_settings.database_path))
    try:
        yield connection
    finally:
        connection.close()
