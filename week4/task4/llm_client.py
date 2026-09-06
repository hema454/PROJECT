import time

import httpx

from config import settings


def chat(messages: list[dict], max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            if settings.llm_provider == "ollama":
                resp = httpx.post(
                    f"{settings.ollama_base_url}/api/chat",
                    json={"model": settings.llm_model, "messages": messages, "stream": False},
                    timeout=60,
                )
                resp.raise_for_status()
                return resp.json()["message"]["content"]
            else:
                resp = httpx.post(
                    f"{settings.openrouter_base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {settings.ai_key}"},
                    json={"model": settings.llm_model, "messages": messages},
                    timeout=60,
                )
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]
        except httpx.HTTPError:
            if attempt == max_retries - 1:
                raise
            time.sleep(2**attempt)