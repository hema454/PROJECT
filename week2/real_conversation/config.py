from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --- OpenRouter ---
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    
    openrouter_models: list[str] = [
        "anthropic/claude-haiku-4.5",         # closed-weight
        "openai/gpt-5-mini",                  # closed-weight
    ]

    