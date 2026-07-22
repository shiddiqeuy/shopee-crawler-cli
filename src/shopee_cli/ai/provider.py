"""AI provider abstraction."""

import os
from typing import Protocol

from shopee_cli.ai.claude_provider import ClaudeProvider
from shopee_cli.ai.deepseek_provider import DeepSeekProvider
from shopee_cli.ai.gemini_provider import GeminiProvider
from shopee_cli.ai.models import AIProviderName, InsightRequest, InsightResponse
from shopee_cli.ai.ollama_provider import OllamaProvider
from shopee_cli.ai.openai_provider import OpenAIProvider
from shopee_cli.ai.openrouter_provider import OpenRouterProvider


class AIProvider(Protocol):
    """Interchangeable AI provider interface."""

    name: AIProviderName
    default_model: str

    def generate(self, request: InsightRequest) -> InsightResponse: ...


def create_provider(provider_name: AIProviderName | str) -> AIProvider:
    """Create an AI provider implementation."""
    name = AIProviderName(provider_name)
    if name == AIProviderName.OPENAI:
        return OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
    if name == AIProviderName.CLAUDE:
        return ClaudeProvider(api_key=os.getenv("ANTHROPIC_API_KEY"))
    if name == AIProviderName.GEMINI:
        return GeminiProvider(api_key=os.getenv("GOOGLE_API_KEY"))
    if name == AIProviderName.OPENROUTER:
        return OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY"))
    if name == AIProviderName.DEEPSEEK:
        return DeepSeekProvider(api_key=os.getenv("DEEPSEEK_API_KEY"))
    return OllamaProvider(base_url=os.getenv("OLLAMA_URL", "http://127.0.0.1:11434"))
