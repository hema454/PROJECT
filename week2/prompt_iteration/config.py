from pathlib import Path

from pydantic_settings import BaseSettings

# Shared .env lives one level up, in the week2/ folder.
SHARED_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    openrouter_base_url: str = "https://openrouter.ai/api/v1/chat/completions"
    openrouter_api_key: str
    model: str = "openai/gpt-4o-mini"

    class Config:
        env_file = SHARED_ENV_PATH
        extra = "ignore"


settings = Settings()