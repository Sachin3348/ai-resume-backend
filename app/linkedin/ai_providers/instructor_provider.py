"""AI provider using the existing instructor client (provider-agnostic)."""

from __future__ import annotations

import asyncio
from functools import partial

from app.llm_client import get_instructor_client, get_model_name
from ..schemas import LinkedInEvaluation
from .base import BaseAIProvider


class InstructorProvider(BaseAIProvider):
    """
    Uses the project's existing instructor client (from_provider).
    This supports Google, OpenAI, Anthropic, Ollama — whatever is configured.
    """

    async def evaluate_profile(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> LinkedInEvaluation:
        client = get_instructor_client()
        model = get_model_name()  # e.g. "gemini-2.5-flash", not "google/gemini-2.5-flash"

        # instructor's create is sync for google-genai; run in thread
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            partial(
                client.chat.completions.create,
                model=model,
                response_model=LinkedInEvaluation,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_retries=2,
            ),
        )
        return result
