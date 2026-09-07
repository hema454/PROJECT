"""
Shared embedding helper for all of week4's tasks.

Lives at week4/ (not inside any individual taskN/ folder) so that every
task imports the SAME embed_text(), guaranteeing the same model is used
at both ingest and query time across tasks -- and so no task depends on
another task's directory layout or its own separate config.py.

The model name is intentionally NOT read from a per-task config.py (that
would just recreate the same coupling problem one level up, depending on
whichever task's config.py happens to be first on sys.path). It can be
overridden via the EMBEDDING_MODEL environment variable if needed;
otherwise it defaults to the model used throughout week4.
"""

import os
from functools import lru_cache

from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_text(text: str) -> list[float]:
    return _get_model().encode(text, normalize_embeddings=True).tolist()