"""Gemini provider."""

from shopee_cli.ai.exceptions import EmptyAIResponseError, MissingAPIKeyError
from shopee_cli.ai.http import post_json
from shopee_cli.ai.models import AIProviderName, InsightRequest, InsightResponse


class GeminiProvider:
    """Google Gemini provider."""

    name = AIProviderName.GEMINI
    default_model = "gemini-1.5-flash"

    def __init__(self, api_key: str | None) -> None:
        self._api_key = api_key

    def generate(self, request: InsightRequest) -> InsightResponse:
        if not self._api_key:
            msg = "GOOGLE_API_KEY is required for Gemini insights."
            raise MissingAPIKeyError(msg)
        response = post_json(
            f"https://generativelanguage.googleapis.com/v1beta/models/{request.model}:generateContent?key={self._api_key}",
            {
                "contents": [
                    {
                        "parts": [
                            {"text": request.prompt.system_prompt},
                            {"text": request.prompt.user_prompt},
                        ]
                    }
                ]
            },
            {},
        )
        candidates = response.get("candidates")
        content = (
            candidates[0].get("content")
            if isinstance(candidates, list) and candidates
            else None
        )
        parts = content.get("parts") if isinstance(content, dict) else None
        text = parts[0].get("text") if isinstance(parts, list) and parts else None
        if not isinstance(text, str) or not text.strip():
            msg = "Gemini returned an empty response."
            raise EmptyAIResponseError(msg)
        return InsightResponse(
            markdown=text.strip(),
            provider=self.name,
            model=request.model,
        )
