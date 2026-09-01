import json
import logging
from typing import Any

import httpx
from json_repair import repair_json

from config import settings

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    pass


def build_prompt(
    text: str, schema_description: str, history: list[dict[str, str]] | None = None
) -> str:
    history_block = ""
    if history:
        lines = [f"{m['role']}: {m['content']}" for m in history]
        history_block = "Previous exchanges in this conversation:\n" + "\n".join(lines) + "\n\n"
    return (
        f"{history_block}"
        "Extract structured data as JSON only, no prose.\n"
        f"Fields to extract: {schema_description}\n\n"
        f"Text:\n{text}"
    )


async def extract(
    text: str, schema_description: str, history: list[dict[str, str]] | None = None
) -> tuple[dict[str, Any], bool]:
    prompt = build_prompt(text, schema_description, history)
    logger.info(
        "extraction requested, prompt_chars=%d, history_messages=%d",
        len(prompt),
        len(history or []),
    )

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

    return data, repaired