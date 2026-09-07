import sys
from pathlib import Path

# points at week4/ (the shared embeddings.py), not the old local task4/embeddings.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings
from db import similarity_search
from embeddings import embed_text


def retrieve(question: str) -> list[dict]:
    q_emb = embed_text(question)
    rows = similarity_search(q_emb, settings.default_k)
    return [r for r in rows if r["distance"] <= settings.similarity_threshold]