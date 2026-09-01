import json
import logging
import uuid
from typing import Any, AsyncIterator

import httpx
from json_repair import repair_json
from sqlalchemy.ext.asyncio import AsyncSession

import repository
from config import settings
from tables import Conversation, Message

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    pass


class ConversationNotFoundError(Exception):
    pass


def _build_prompt(
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
    prompt = _build_prompt(text, schema_description, history)
    # Log length/counts only -- never the prompt or history content.
    logger.info(
        "extraction requested, prompt_chars=%d, history_messages=%d", len(prompt), len(history or [])
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

    field_count = len(data) if isinstance(data, dict) else -1
    logger.info("extraction complete, repaired=%s, field_count=%d", repaired, field_count)
    return data, repaired


async def extract_stream(
    text: str, schema_description: str, history: list[dict[str, str]] | None = None
) -> AsyncIterator[str]:
    prompt = _build_prompt(text, schema_description, history)
    logger.info(
        "streaming extraction requested, prompt_chars=%d, history_messages=%d",
        len(prompt), len(history or []),
    )

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


# --- Conversation persistence: owns transactions here; repository.py just runs queries ---


async def get_or_create_conversation(
    session: AsyncSession, tenant_id: uuid.UUID, conversation_id: uuid.UUID | None
) -> Conversation:
    async with session.begin():
        if conversation_id is not None:
            existing = await repository.get_conversation_by_id(session, tenant_id, conversation_id)
            if existing is not None:
                return existing
        return await repository.insert_conversation(session, tenant_id)


async def get_conversation_history(
    session: AsyncSession, tenant_id: uuid.UUID, conversation_id: uuid.UUID
) -> list[dict[str, str]]:
    messages = await repository.list_messages_for_conversation(session, tenant_id, conversation_id)
    return [{"role": m.role, "content": m.content} for m in messages]


async def record_exchange(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    conversation_id: uuid.UUID,
    user_text: str,
    assistant_content: str,
) -> None:
    async with session.begin():
        await repository.insert_message(
            session, tenant_id, conversation_id, role="user", content=user_text
        )
        await repository.insert_message(
            session, tenant_id, conversation_id, role="assistant", content=assistant_content
        )


async def replay_conversation(
    session: AsyncSession, tenant_id: uuid.UUID, conversation_id: uuid.UUID
) -> tuple[Conversation, list[Message]]:
    conversation = await repository.get_conversation_by_id(session, tenant_id, conversation_id)
    if conversation is None:
        raise ConversationNotFoundError(str(conversation_id))
    messages = await repository.list_messages_for_conversation(session, tenant_id, conversation_id)
    return conversation, messages