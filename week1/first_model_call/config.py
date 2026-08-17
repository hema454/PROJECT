

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openrouter_api_key: str

    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    model: str = "google/gemini-2.5-flash-lite"
    temperature: float = 1.3

    usd_to_inr: float = 88.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

