"""AI insight exceptions."""


class AIInsightError(Exception):
    """Base AI insight error."""


class MissingAPIKeyError(AIInsightError):
    """Raised when a provider API key is missing."""


class ProviderUnavailableError(AIInsightError):
    """Raised when a provider cannot be reached."""


class ProviderTimeoutError(AIInsightError):
    """Raised when a provider request times out."""


class ProviderRateLimitError(AIInsightError):
    """Raised when a provider returns rate limiting."""


class InvalidAIResponseError(AIInsightError):
    """Raised when a provider response cannot be parsed."""


class EmptyAIResponseError(AIInsightError):
    """Raised when a provider returns no report text."""


class UnsupportedAIProviderError(AIInsightError):
    """Raised when an unsupported provider is requested."""


class InsightSnapshotNotFoundError(AIInsightError):
    """Raised when no analyzable snapshot exists."""
