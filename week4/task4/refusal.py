REFUSAL_MESSAGE = "I don't know — the corpus doesn't contain information relevant to this question."


def check_refusal(chunks: list[dict]) -> tuple[bool, str | None]:
    if not chunks:
        return True, REFUSAL_MESSAGE
    return False, None