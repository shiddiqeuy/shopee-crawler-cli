"""Ollama provider."""

from shopee_cli.ai.exceptions import EmptyAIResponseError
from shopee_cli.ai.http import post_json
from shopee_cli.ai.models import AIProviderName, InsightRequest, InsightResponse


class OllamaProvider:
    """Local Ollama chat provider."""

    name = AIProviderName.OLLAMA
    default_model = "llama3.1"

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    def generate(self, request: InsightRequest) -> InsightResponse:
        response = post_json(
            f"{self._base_url}/api/chat",
            {
                "model": request.model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": request.prompt.system_prompt},
                    {"role": "user", "content": request.prompt.user_prompt},
                ],
            },
            {},
        )
        message = response.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str) or not content.strip():
            msg = "Ollama returned an empty response."
            raise EmptyAIResponseError(msg)
        return InsightResponse(
            markdown=content.strip(), provider=self.name, model=request.model
        )
