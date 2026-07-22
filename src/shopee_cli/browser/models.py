"""Typed browser models."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class BrowserMode(StrEnum):
    """Supported browser modes."""

    MAIN = "main"
    ISOLATED = "isolated"


class ConnectionState(StrEnum):
    """Browser connection states."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


class LoginStatus(StrEnum):
    """Best-effort Shopee login states."""

    LOGGED_IN = "logged_in"
    LOGGED_OUT = "logged_out"
    UNKNOWN = "unknown"


class TabInfo(BaseModel):
    """Safe browser tab information."""

    model_config = ConfigDict(frozen=True)

    index: int
    title: str
    url: str
    is_active: bool
    is_shopee: bool
    login_status: LoginStatus = LoginStatus.UNKNOWN


class BrowserStatus(BaseModel):
    """Browser connection status."""

    model_config = ConfigDict(frozen=True)

    mode: BrowserMode
    state: ConnectionState
    context_count: int = 0
    page_count: int = 0
    shopee_tab_count: int = 0
    login_status: LoginStatus = LoginStatus.UNKNOWN
    message: str | None = None
