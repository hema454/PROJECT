from pathlib import Path

from pydantic_settings import BaseSettings

# .env lives in the week4 root, one level above this file's folder (task4/),
# so resolve it relative to this file rather than the current working directory.
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    database_url: str
    embedding_model: str
    embedding_dim: int = 384
    llm_provider: str  # "ollama" or "openrouter"
    llm_model: str
    ollama_base_url: str
    ai_key: str = ""
    openrouter_base_url: str
    default_k: int = 5
    similarity_threshold: float = 0.35  # max cosine distance to accept a chunk
    max_history_tokens: int = 2000
    doc_link_base: str

    class Config:
        env_file = ENV_PATH
        extra = "ignore"


settings = Settings()