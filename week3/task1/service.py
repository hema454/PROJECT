import json
import logging
from typing import Any, AsyncIterator

import httpx
from json_repair import repair_json

from config import settings

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    pass


def _build_prompt(text: str, schema_description: str) -> str:
    return (
        "Extract structured data as JSON only, no prose.\n"
        f"Fields to extract: {schema_description}\n\n"
        f"Text:\n{text}"
    )


async def extract(text: str, schema_description: str) -> tuple[dict[str, Any], bool]:
    prompt = _build_prompt(text, schema_description)
    # Log length only -- never the prompt itself.
    logger.info("extraction requested, prompt_chars=%d", len(prompt))

    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": settings.temperature},
    }

    async with httpx.AsyncClient(timeout=settings.timeout_seconds) as client:
        try:
            resp = await client.post(f"{settings.ollama_base_url}/api/generate", json=payload)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("ollama call failed, type=%s", type(exc).__name__)
            raise ExtractionError("model call failed") from exc

    raw = resp.json().get("response", "")
    repaired = False
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("model output was not valid json, repairing")
        data = json.loads(repair_json(raw))
        repaired = True

    field_count = len(data) if isinstance(data, dict) else -1
    logger.info("extraction complete, repaired=%s, field_count=%d", repaired, field_count)
    return data, repaired


async def extract_stream(text: str, schema_description: str) -> AsyncIterator[str]:
    prompt = _build_prompt(text, schema_description)
    logger.info("streaming extraction requested, prompt_chars=%d", len(prompt))

    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": True,
        "options": {"temperature": settings.temperature},
    }

    token_count = 0
    async with httpx.AsyncClient(timeout=settings.timeout_seconds) as client:
        try:
            async with client.stream(
                "POST", f"{settings.ollama_base_url}/api/generate", json=payload
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    token = chunk.get("response", "")
                    if token:
                        token_count += 1
                        yield token
                    if chunk.get("done"):
                        break
        except httpx.HTTPError as exc:
            logger.error("ollama streaming call failed, type=%s", type(exc).__name__)
            raise ExtractionError("model call failed") from exc

    logger.info("streaming extraction complete, token_count=%d", token_count)