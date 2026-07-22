"""AI insight models."""

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from shopee_cli.analytics.models import AnalyticsReport


class AIProviderName(StrEnum):
    """Supported AI providers."""

    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"


class InsightPrompt(BaseModel):
    """Provider-ready prompt payload."""

    model_config = ConfigDict(frozen=True)

    system_prompt: str
    user_prompt: str
    analytics_json: str


class InsightRequest(BaseModel):
    """AI insight generation request."""

    model_config = ConfigDict(frozen=True)

    provider: AIProviderName
    model: str
    prompt: InsightPrompt


class InsightResponse(BaseModel):
    """AI provider response."""

    model_config = ConfigDict(frozen=True)

    markdown: str
    provider: AIProviderName
    model: str


class InsightResult(BaseModel):
    """Generated insight report result."""

    model_config = ConfigDict(frozen=True)

    report: AnalyticsReport
    provider: AIProviderName
    model: str
    output_path: Path
    duration_seconds: float
    markdown: str
