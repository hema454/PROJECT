"""
Embeds text using a local sentence-transformers model instead of a paid
API. Loaded once at import time (model download happens on first run,
then it's cached locally -- no internet needed after that).
"""

from sentence_transformers import SentenceTransformer

from config import settings

_model = SentenceTransformer(settings.embedding_model)


def embed_text(text: str) -> list[float]:
    """Embed a single string using the configured local embedding model."""
    vector = _model.encode(text, convert_to_numpy=True)
    return vector.tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed multiple strings in one call. Use this when loading chunks (task 1)."""
    vectors = _model.encode(texts, convert_to_numpy=True)
    return [v.tolist() for v in vectors]