"""Application settings loaded from environment / .env file."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    groq_api_key: str = ""
    groq_extraction_model: str = "llama-3.3-70b-versatile"
    # gemma2-9b-it (named in the assignment) was decommissioned by Groq;
    # llama-3.1-8b-instant is the current small/fast equivalent.
    groq_fast_model: str = "llama-3.1-8b-instant"

    database_url: str = "sqlite:///./complaints.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
