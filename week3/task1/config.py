from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    ollama_base_url: str 
    ollama_model: str = "llama3.1:8b"
    temperature: float = 0.0
    api_key: str
    timeout_seconds: float = 60.0
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")


settings = Settings()