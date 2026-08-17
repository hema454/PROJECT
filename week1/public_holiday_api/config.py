from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    nager_base_url: str = "https://date.nager.at/api/v3"
    request_timeout_seconds: float = 10.0
    max_retries: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()