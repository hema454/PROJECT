"""
Conversation history storage.

LIMITATION: history is kept in a module-level dict (`_histories`), entirely
in-memory within a single Python process. This means:

  - Restarting the server wipes all conversation history for every
    conversation_id -- there is no persistence layer behind it.
  - In any multi-worker deployment (e.g. uvicorn/gunicorn with more than
    one worker process), each worker holds its own separate `_histories`
    dict. The same conversation_id can land on a different worker between
    requests, in which case it will appear to have no history at all, even
    mid-conversation.

This is acceptable for local development and single-process testing, but
is NOT safe for production/multi-worker use as-is. A real deployment
should replace `_histories` with an external store (e.g. Redis, or a DB
table keyed by conversation_id) shared across all worker processes.
"""

import tiktoken

from config import settings
from llm_client import chat

_histories: dict[str, list[dict]] = {}
_encoding = tiktoken.get_encoding("cl100k_base")


def _count_tokens(messages: list[dict]) -> int:
    return sum(len(_encoding.encode(m["content"])) for m in messages)


def get_history(conversation_id: str) -> list[dict]:
    return _histories.get(conversation_id, [])


def add_turn(conversation_id: str, user_msg: str, assistant_msg: str):
    history = _histories.setdefault(conversation_id, [])
    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": assistant_msg})
    _enforce_budget(conversation_id)


def _enforce_budget(conversation_id: str):
    history = _histories[conversation_id]
    while _count_tokens(history) > settings.max_history_tokens and len(history) > 2:
        old_chunk = history[:4]
        summary = chat(
            [
                {
                    "role": "system",
                    "content": "Summarize this exchange in 2 sentences, preserving key facts.",
                },
                {"role": "user", "content": str(old_chunk)},
            ]
        )
        _histories[conversation_id] = [
            {"role": "system", "content": f"Earlier conversation summary: {summary}"}
        ] + history[4:]
        history = _histories[conversation_id]