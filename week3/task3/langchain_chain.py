import json
import logging
from typing import Any

from json_repair import repair_json
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable
from langchain_ollama import ChatOllama

from config import settings

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    pass


# legacy_chain.py sends a single "prompt" string to Ollama's /api/generate
# endpoint — no separate system/user split. To match that exactly, this is
# a single human message, not a system+human pair.
PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "human",
            "{history_block}"
            "Extract structured data as JSON only, no prose.\n"
            "Fields to extract: {schema_description}\n\n"
            "Text:\n{text}",
        ),
    ]
)


class RepairingJsonOutputParser(BaseOutputParser[dict[str, Any]]):
    """Parses model output as JSON, falling back to json_repair on failure.

    Mirrors legacy_chain.extract()'s parsing step. Since BaseOutputParser.parse()
    returns a single value, the repair flag is smuggled into the dict under the
    private key "_repaired" and popped back out in extract() below.
    """

    def parse(self, text: str) -> dict[str, Any]:
        try:
            data = json.loads(text)
            data["_repaired"] = False
        except json.JSONDecodeError:
            logger.warning("model output was not valid json, repairing")
            data = json.loads(repair_json(text))
            data["_repaired"] = True
        return data

    @property
    def _type(self) -> str:
        return "repairing_json_output_parser"


def _build_history_block(history: list[dict[str, str]] | None) -> str:
    if not history:
        return ""
    lines = [f"{m['role']}: {m['content']}" for m in history]
    return "Previous exchanges in this conversation:\n" + "\n".join(lines) + "\n\n"


def build_chain() -> RunnableSerializable:
    # legacy_chain.py POSTs to Ollama's /api/generate (raw completion) endpoint.
    # ChatOllama instead calls /api/chat under the hood — a different endpoint
    # with a different wire format. See comparison.md for why that's still fine.
    llm = ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=settings.temperature,
        format="json",
        timeout=settings.timeout_seconds,
    )
    return PROMPT | llm | RepairingJsonOutputParser()


async def extract(
    text: str, schema_description: str, history: list[dict[str, str]] | None = None
) -> tuple[dict[str, Any], bool]:
    history_block = _build_history_block(history)
    logger.info(
        "extraction requested, schema_chars=%d, history_messages=%d",
        len(schema_description),
        len(history or []),
    )

    chain = build_chain()

    try:
        
        result = await chain.ainvoke(
            {
                "history_block": history_block,
                "schema_description": schema_description,
                "text": text,
            }
        )
    except Exception as exc:
        logger.error("ollama call failed, type=%s", type(exc).__name__)
        raise ExtractionError("model call failed") from exc

    repaired = result.pop("_repaired", False)
    return result, repaired