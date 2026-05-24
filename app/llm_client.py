import os
import instructor
from functools import lru_cache
from app.config import get_settings

_PROVIDER_KEY_ATTR = {
    "google": "google_api_key",
    "openai": "openai_api_key",
    "anthropic": "anthropic_api_key",
}


def _get_api_key(settings) -> str | None:
    """Return the API key for the active provider, or None for keyless providers (Ollama)."""
    provider_prefix = settings.llm_provider.split("/")[0].lower()
    attr = _PROVIDER_KEY_ATTR.get(provider_prefix)
    if attr is None:
        return None  # Ollama — no key needed

    key_value = getattr(settings, attr, "")
    if not key_value:
        raise ValueError(
            f"API key for provider '{provider_prefix}' is missing. "
            f"Set {attr.upper()} in your .env file."
        )
    return key_value


@lru_cache
def get_instructor_client() -> instructor.Instructor:
    """
    Singleton Instructor client initialized via the provider-agnostic
    `instructor.from_provider()` interface.

    api_key is passed explicitly to from_provider so the underlying SDK
    receives it directly — independent of os.environ timing.
    """
    settings = get_settings()
    api_key = _get_api_key(settings)

    kwargs = {}
    if api_key:
        kwargs["api_key"] = api_key

    client = instructor.from_provider(settings.llm_provider, **kwargs)
    return client


def get_model_name() -> str:
    """Return the model portion of the provider string (after the slash)."""
    settings = get_settings()
    parts = settings.llm_provider.split("/", 1)
    return parts[1] if len(parts) == 2 else settings.llm_provider

    """Return the model portion of the provider string (after the slash)."""
    settings = get_settings()
    parts = settings.llm_provider.split("/", 1)
    return parts[1] if len(parts) == 2 else settings.llm_provider
