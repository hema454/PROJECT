import re


def chunk_fixed(text: str, size: int, overlap: int) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + size])
        start += size - overlap
    return [c for c in chunks if c.strip()]


def chunk_sentence_window(text: str, sentences_per_chunk: int = 3) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk = " ".join(sentences[i : i + sentences_per_chunk])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


# A: small, no overlap. B: your Task 4.4 default (800/100 overlap). C: sentence-window.
STRATEGIES = {
    "chunks_a": lambda text: chunk_fixed(text, size=300, overlap=0),
    "chunks_b": lambda text: chunk_fixed(text, size=800, overlap=100),
    "chunks_c": lambda text: chunk_sentence_window(text, sentences_per_chunk=3),
}