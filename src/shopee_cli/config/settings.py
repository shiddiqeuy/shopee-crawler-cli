"""Application settings."""

from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from shopee_cli.browser.models import BrowserMode


class Settings(BaseSettings):
    """Runtime configuration loaded from defaults and .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="SHOPEE_",
        populate_by_name=True,
    )

    environment: str = Field(default="local")
    browser_mode: BrowserMode = Field(
        default=BrowserMode.MAIN,
        validation_alias=AliasChoices("SHOPEE_BROWSER_MODE", "BROWSER_MODE"),
    )
    browser_cdp_url: str = Field(
        default="http://127.0.0.1:9222",
        validation_alias=AliasChoices("SHOPEE_BROWSER_CDP_URL", "BROWSER_CDP_URL"),
    )
    browser_profile_path: Path = Field(
        default=Path("data/browser-profile"),
        validation_alias=AliasChoices(
            "SHOPEE_BROWSER_PROFILE_PATH",
            "BROWSER_PROFILE_PATH",
        ),
    )
    browser_headless: bool = Field(
        default=False,
        validation_alias=AliasChoices("SHOPEE_BROWSER_HEADLESS", "BROWSER_HEADLESS"),
    )
    browser_timeout_ms: int = Field(
        default=30000,
        validation_alias=AliasChoices(
            "SHOPEE_BROWSER_TIMEOUT_MS",
            "BROWSER_TIMEOUT_MS",
        ),
    )
    database_dir: Path = Field(default=Path("data/database"))
    export_path: Path = Field(default=Path("data/exports"))
    log_dir: Path = Field(default=Path("logs"))
    database_file_name: str = Field(default="shopee_market.duckdb")

    @property
    def database_path(self) -> Path:
        """Return the DuckDB database file path."""
        return self.database_dir / self.database_file_name

    @field_validator("browser_timeout_ms")
    @classmethod
    def validate_browser_timeout_ms(cls, value: int) -> int:
        """Validate browser timeout values."""
        if value <= 0:
            msg = "Browser timeout must be greater than 0 milliseconds."
            raise ValueError(msg)
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
