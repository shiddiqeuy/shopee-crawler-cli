"""Browser domain exceptions."""


class BrowserError(Exception):
    """Base browser error."""


class BrowserConnectionError(BrowserError):
    """Raised when a browser connection fails."""


class BrowserNotAvailableError(BrowserConnectionError):
    """Raised when the configured browser endpoint is unavailable."""


class InvalidBrowserModeError(BrowserError):
    """Raised when an unsupported browser mode is requested."""


class ShopeeTabNotFoundError(BrowserError):
    """Raised when no Shopee tab is available."""
