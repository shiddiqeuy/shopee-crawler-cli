"""Minimal provider HTTP helpers."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from shopee_cli.ai.exceptions import (
    InvalidAIResponseError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)


def post_json(
    url: str,
    payload: dict[str, object],
    headers: dict[str, str],
    timeout: int = 60,
) -> dict[str, object]:
    """Send a JSON POST request and return parsed JSON."""
    request = Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            raw_body = response.read().decode("utf-8")
    except HTTPError as error:
        if error.code == 429:
            msg = "AI provider rate limit was reached."
            raise ProviderRateLimitError(msg) from error
        msg = f"AI provider returned HTTP {error.code}."
        raise ProviderUnavailableError(msg) from error
    except TimeoutError as error:
        msg = "AI provider request timed out."
        raise ProviderTimeoutError(msg) from error
    except (URLError, OSError) as error:
        msg = "AI provider is unavailable."
        raise ProviderUnavailableError(msg) from error

    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError as error:
        msg = "AI provider returned invalid JSON."
        raise InvalidAIResponseError(msg) from error
    if not isinstance(parsed, dict):
        msg = "AI provider returned an invalid response shape."
        raise InvalidAIResponseError(msg)
    return parsed
