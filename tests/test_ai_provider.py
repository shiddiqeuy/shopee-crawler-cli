"""AI provider abstraction tests."""

import pytest

from shopee_cli.ai.exceptions import MissingAPIKeyError
from shopee_cli.ai.models import AIProviderName, InsightRequest
from shopee_cli.ai.openai_provider import OpenAIProvider
from shopee_cli.ai.prompt_builder import InsightPrompt
from shopee_cli.ai.provider import create_provider


def test_provider_factory_supports_all_providers(monkeypatch) -> None:
    """Provider abstraction creates supported implementations."""
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    monkeypatch.setenv("GOOGLE_API_KEY", "x")
    monkeypatch.setenv("OPENROUTER_API_KEY", "x")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "x")

    for provider in AIProviderName:
        assert create_provider(provider).name == provider


def test_openai_provider_requires_api_key() -> None:
    """Missing API keys fail before network access."""
    request = InsightRequest(
        provider=AIProviderName.OPENAI,
        model="test",
        prompt=InsightPrompt(system_prompt="s", user_prompt="u", analytics_json="{}"),
    )

    with pytest.raises(MissingAPIKeyError):
        OpenAIProvider(api_key=None).generate(request)
