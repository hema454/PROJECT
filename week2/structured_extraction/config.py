"""
config.py

Settings for calling a local open-weight model via Ollama, where these
malformed-JSON failures actually happen (unlike hosted frontier models,
which rarely produce them).
"""

from pathlib import Path

from pydantic_settings import BaseSettings

# Shared .env lives one level up, in the week2/ folder.
SHARED_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434/api/chat"
    ollama_model: str = "llama3.1:8b"   # swap for whatever small model you have pulled
    num_runs: int = 50

    class Config:
        env_file = SHARED_ENV_PATH
        extra = "ignore"  # shared .env has keys from other projects — ignore, don't error


settings = Settings()