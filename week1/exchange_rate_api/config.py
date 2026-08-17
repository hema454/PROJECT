from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    exchange_rate_base_url: str = "https://open.er-api.com/v6"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()