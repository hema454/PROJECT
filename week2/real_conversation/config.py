from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Shared .env lives one level up, in the week2/ folder.
SHARED_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=SHARED_ENV_PATH, env_file_encoding="utf-8", extra="ignore")

    # --- OpenRouter ---
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # --- Chat behavior ---
    primary_model: str = "openai/gpt-5-mini"
    fallback_model: str = "meta-llama/llama-3.3-70b-instruct"
    system_prompt: str = "You are a helpful, concise assistant."
    max_tokens: int = 1024

    # --- Pricing (USD per million tokens) ---
    pricing: dict[str, dict[str, float]] = {
        "openai/gpt-5-mini": {"input": 0.25, "output": 2.00},
        "meta-llama/llama-3.3-70b-instruct": {"input": 0.10, "output": 0.32},
    }


settings = Settings()