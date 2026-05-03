from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env files."""

    app_name: str = "Q-Commerce AI"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    data_dir: Path = Path("data")
    raw_data_dir: Path = Path("data/raw")
    processed_data_dir: Path = Path("data/processed")
    model_dir: Path = Path("models/artifacts")

    openai_api_key: str | None = None
    database_url: str | None = None
    redis_url: str | None = None

    default_service_radius_km: float = Field(default=3.0, gt=0)
    default_delivery_sla_minutes: int = Field(default=15, gt=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
