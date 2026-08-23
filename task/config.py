"""
config.py

Settings for this project. Combines:
  - PostgreSQL connection (used by db.py / store.py to fetch prompts)
  - OpenRouter settings (used by open_router.py to call models)

Reads from a .env file in this same folder — create
D:\workspace\project\task\.env with:

    PG_HOST=localhost
    PG_PORT=5432
    PG_DATABASE=prompt_store
    PG_USER=postgres
    PG_PASSWORD=your_password_here

    OPENROUTER_API_KEY=sk-or-v1-...

OPENROUTER_MODELS and OPENROUTER_BASE_URL are optional — defaults below
are used unless overridden in .env.
"""

from pathlib import Path

from pydantic_settings import BaseSettings

# .env lives in this same folder (task/)
ENV_PATH = Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    # --- PostgreSQL (for store.py / db.py) ---
    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_database: str = "prompt_store"
    pg_user: str = "postgres"
    pg_password: str

    # --- OpenRouter (for open_router.py) ---
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_models: list[str] = [
        "openai/gpt-4o-mini",
    ]
    max_output_tokens: int = 512
    request_timeout_s: float = 30.0

    class Config:
        env_file = ENV_PATH
        extra = "ignore"

    @property
    def connection_string(self) -> str:
        return (
            f"host={self.pg_host} port={self.pg_port} "
            f"dbname={self.pg_database} user={self.pg_user} password={self.pg_password}"
        )


settings = Settings()