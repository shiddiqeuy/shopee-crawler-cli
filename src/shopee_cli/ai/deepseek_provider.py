"""DeepSeek provider."""

from shopee_cli.ai.exceptions import MissingAPIKeyError
from shopee_cli.ai.http import post_json
from shopee_cli.ai.models import AIProviderName, InsightRequest, InsightResponse
from shopee_cli.ai.openai_provider import _extract_openai_text


class DeepSeekProvider:
    """DeepSeek chat completions provider."""

    name = AIProviderName.DEEPSEEK
    default_model = "deepseek-chat"

    def __init__(self, api_key: str | None) -> None:
        self._api_key = api_key

    def generate(self, request: InsightRequest) -> InsightResponse:
        if not self._api_key:
            msg = "DEEPSEEK_API_KEY is required for DeepSeek insights."
            raise MissingAPIKeyError(msg)
        response = post_json(
            "https://api.deepseek.com/chat/completions",
            {
                "model": request.model,
                "messages": [
                    {"role": "system", "content": request.prompt.system_prompt},
                    {"role": "user", "content": request.prompt.user_prompt},
                ],
            },
            {"Authorization": f"Bearer {self._api_key}"},
        )
        return InsightResponse(
            markdown=_extract_openai_text(response),
            provider=self.name,
            model=request.model,
        )
