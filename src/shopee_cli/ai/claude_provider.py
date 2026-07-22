"""Claude provider."""

from shopee_cli.ai.exceptions import EmptyAIResponseError, MissingAPIKeyError
from shopee_cli.ai.http import post_json
from shopee_cli.ai.models import AIProviderName, InsightRequest, InsightResponse


class ClaudeProvider:
    """Anthropic Claude messages provider."""

    name = AIProviderName.CLAUDE
    default_model = "claude-3-5-haiku-latest"

    def __init__(self, api_key: str | None) -> None:
        self._api_key = api_key

    def generate(self, request: InsightRequest) -> InsightResponse:
        if not self._api_key:
            msg = "ANTHROPIC_API_KEY is required for Claude insights."
            raise MissingAPIKeyError(msg)
        response = post_json(
            "https://api.anthropic.com/v1/messages",
            {
                "model": request.model,
                "max_tokens": 1800,
                "system": request.prompt.system_prompt,
                "messages": [{"role": "user", "content": request.prompt.user_prompt}],
            },
            {
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        content = response.get("content")
        text = content[0].get("text") if isinstance(content, list) and content else None
        if not isinstance(text, str) or not text.strip():
            msg = "Claude returned an empty response."
            raise EmptyAIResponseError(msg)
        return InsightResponse(
            markdown=text.strip(),
            provider=self.name,
            model=request.model,
        )
