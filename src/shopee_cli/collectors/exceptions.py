"""Search collector exceptions."""


class SearchCollectorError(Exception):
    """Base search collector error."""


class InvalidKeywordError(SearchCollectorError):
    """Raised when a search keyword is invalid."""


class SearchPageLoadError(SearchCollectorError):
    """Raised when a search page cannot be loaded."""


class ProductCardNotFoundError(SearchCollectorError):
    """Raised when product cards cannot be identified."""


class SearchVerificationRequiredError(SearchCollectorError):
    """Raised when Shopee requires manual verification."""


class SearchTimeoutError(SearchCollectorError):
    """Raised when collection times out."""


class SearchPersistenceError(SearchCollectorError):
    """Raised when search results cannot be persisted."""


class UnsupportedSortModeError(SearchCollectorError):
    """Raised when a sort mode is accepted by CLI but not safely implemented."""
