from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# .env lives at the week4 root, one level up from this task's subfolder —
# resolve it explicitly so it works regardless of which directory scripts run from.
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_PATH, env_file_encoding="utf-8")

    # Postgres connection
    database_url: str

    # Embedding model
    ai_key: str
    embedding_model: str
    embedding_dim: int

    # Search defaults
    default_k: int


settings = Settings()