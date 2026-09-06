from config import settings
from db import similarity_search
from embeddings import embed_text


def retrieve(question: str) -> list[dict]:
    q_emb = embed_text(question)
    rows = similarity_search(q_emb, settings.default_k)
    return [r for r in rows if r["distance"] <= settings.similarity_threshold]