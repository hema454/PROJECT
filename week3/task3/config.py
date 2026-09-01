from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    temperature: float = 0.0
    timeout_seconds: float = 60.0
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/extraction_service"

    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")


settings = Settings()