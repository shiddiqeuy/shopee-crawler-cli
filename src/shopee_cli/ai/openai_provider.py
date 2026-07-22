"""OpenAI provider."""

from shopee_cli.ai.exceptions import EmptyAIResponseError, MissingAPIKeyError
from shopee_cli.ai.http import post_json
from shopee_cli.ai.models import AIProviderName, InsightRequest, InsightResponse


class OpenAIProvider:
    """OpenAI chat completions provider."""

    name = AIProviderName.OPENAI
    default_model = "gpt-4o-mini"

    def __init__(self, api_key: str | None) -> None:
        self._api_key = api_key

    def generate(self, request: InsightRequest) -> InsightResponse:
        """Generate an insight report."""
        if not self._api_key:
            msg = "OPENAI_API_KEY is required for OpenAI insights."
            raise MissingAPIKeyError(msg)
        response = post_json(
            "https://api.openai.com/v1/chat/completions",
            {
                "model": request.model,
                "messages": [
                    {"role": "system", "content": request.prompt.system_prompt},
                    {"role": "user", "content": request.prompt.user_prompt},
                ],
            },
            {"Authorization": f"Bearer {self._api_key}"},
        )
        markdown = _extract_openai_text(response)
        return InsightResponse(
            markdown=markdown, provider=self.name, model=request.model
        )


def _extract_openai_text(response: dict[str, object]) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        msg = "OpenAI returned an empty response."
        raise EmptyAIResponseError(msg)
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        msg = "OpenAI returned an empty response."
        raise EmptyAIResponseError(msg)
    return content.strip()
