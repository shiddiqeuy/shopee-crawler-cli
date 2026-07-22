"""Application settings."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from defaults and .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="SHOPEE_",
    )

    environment: str = Field(default="local")
    browser_profile_path: Path = Field(default=Path("data/browser-profile"))
    database_dir: Path = Field(default=Path("data/database"))
    export_path: Path = Field(default=Path("data/exports"))
    log_dir: Path = Field(default=Path("logs"))
    database_file_name: str = Field(default="shopee_market.duckdb")

    @property
    def database_path(self) -> Path:
        """Return the DuckDB database file path."""
        return self.database_dir / self.database_file_name


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
