import json
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    ollama_base_url: str
    ollama_model: str = "llama3.1:8b"
    temperature: float = 0.0
    timeout_seconds: float = 60.0
    log_level: str = "INFO"
    database_url: str
    tenant_api_keys: str = "{}"

    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")

    @property
    def tenant_map(self) -> dict[str, str]:
        return json.loads(self.tenant_api_keys)


settings = Settings()