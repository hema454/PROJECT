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