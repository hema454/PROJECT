
import re

from json_repair import repair_json
from pydantic import BaseModel


class RecoveryError(Exception):
    """Raised when no usable JSON object could be recovered from the text."""


def strip_markdown_fences(text: str) -> str:
    """Removes ```json ... ``` or plain ``` ... ``` wrapping."""
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r"```", "", text)
    return text.strip()


def extract_json_substring(text: str) -> str:
    """Cuts out everything before the first { and after the last }.
    Handles prose-before-JSON. If the response was truncated mid-object
    (no closing brace at all), this just returns from the first { onward
    and lets repair_json attempt to close it."""
    start = text.find("{")
    if start == -1:
        return text
    end = text.rfind("}")
    if end == -1 or end < start:
        return text[start:]
    return text[start:end + 1]


def clean_and_repair(text: str) -> dict:
    """Runs the full pipeline and returns a plain dict."""
    cleaned = strip_markdown_fences(text)
    cleaned = extract_json_substring(cleaned)
    repaired = repair_json(cleaned, return_objects=True)
    if not isinstance(repaired, dict) or not repaired:
        raise RecoveryError(f"Could not recover a JSON object from: {text[:200]!r}")
    return repaired


def parse_and_validate(text: str, model_cls: type[BaseModel]) -> BaseModel:
    """Recovers a dict from raw model output, then validates it against
    the given Pydantic model. Raises RecoveryError or ValidationError —
    callers decide how to handle each."""
    data = clean_and_repair(text)
    return model_cls(**data)