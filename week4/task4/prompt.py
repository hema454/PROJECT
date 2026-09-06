SYSTEM_PROMPT = (
    "You are a grounded assistant. Answer ONLY using the numbered context chunks below. "
    "Cite the chunk number(s) you used inline as [1], [2], etc. "
    'If the context does not contain the answer, say exactly: '
    '"I don\'t know based on the provided documents." Do not use outside knowledge.'
)


def build_prompt(question: str, chunks: list[dict], history: list[dict]) -> list[dict]:
    context_block = "\n\n".join(
        f"[{i + 1}] (from {c['doc_name']}, page {c['page']}):\n{c['content']}"
        for i, c in enumerate(chunks)
    )
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append(
        {"role": "user", "content": f"Context:\n{context_block}\n\nQuestion: {question}"}
    )
    return messages