from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    ollama_base_url: str 
    ollama_model: str = "llama3.1:8b"
    temperature: float = 0.0
    timeout_seconds: float = 60.0
    log_level: str = "INFO"
    api_key: str

    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")


settings = Settings()