from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# .env lives at the week4 root, one level up from this task's subfolder —
# resolve it explicitly so it works regardless of which directory scripts run from.
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    # extra="ignore": the shared .env at the week4 root has keys used by
    # OTHER tasks (llm_provider, ollama_base_url, etc.) that this task's
    # Settings doesn't declare. Without this, pydantic-settings rejects
    # the whole file for any key it doesn't recognize.
    model_config = SettingsConfigDict(env_file=_ENV_PATH, env_file_encoding="utf-8", extra="ignore")

    # Postgres connection
    database_url: str

    # Embedding model
    ai_key: str
    embedding_model: str
    embedding_dim: int

    # Search defaults
    default_k: int


settings = Settings()