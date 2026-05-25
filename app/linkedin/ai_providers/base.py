"""Abstract AI provider interface."""

from __future__ import annotations
from abc import ABC, abstractmethod
from ..schemas import LinkedInEvaluation


class BaseAIProvider(ABC):
    """Abstract base for AI evaluation providers."""

    @abstractmethod
    async def evaluate_profile(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> LinkedInEvaluation:
        """Send prompts to AI and return validated evaluation."""
        ...
