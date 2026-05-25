from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    llm_provider: str = "google/gemini-2.5-flash"
    google_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_semantic_url: str = "redis://localhost:6379/1"
    cache_ttl_days: int = 7
    semantic_distance_threshold: float = 0.10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
