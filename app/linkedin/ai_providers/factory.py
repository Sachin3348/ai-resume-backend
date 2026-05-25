"""AI provider factory."""

from __future__ import annotations

from .base import BaseAIProvider
from .instructor_provider import InstructorProvider


def get_ai_provider() -> BaseAIProvider:
    """
    Return the configured AI provider.
    Currently uses the unified instructor provider which supports
    all configured backends (Google, OpenAI, Anthropic, Ollama).
    
    To add a dedicated provider (e.g. direct httpx to Claude API),
    add a new class extending BaseAIProvider and select here based on config.
    """
    return InstructorProvider()
