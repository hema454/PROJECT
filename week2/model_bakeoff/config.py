
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    
    openrouter_models: list[str] = [
        "meta-llama/llama-3.3-70b-instruct",  
        "qwen/qwen3-coder",                   
        "anthropic/claude-haiku-4.5",         
        "openai/gpt-5-mini",                  
    ]

   
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    
    max_retries: int = 3
    request_timeout_s: float = 60.0
    max_output_tokens: int = 800


settings = Settings()