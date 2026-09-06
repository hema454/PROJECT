import json
from pathlib import Path

from db import get_connection, init_db
from embeddings import embed_batch
from models import ChunkIn

CHUNK_SETS_DIR = Path(__file__).parent / "data" / "chunk_sets"

# Expected format per file: a JSON list of objects like:
# [{"content": "...", "source": "manual.pdf", "page": 3, "metadata": {"category": "billing"}}, ...]


def load_chunk_set(path: Path) -> list[ChunkIn]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [ChunkIn(**item) for item in raw]


def insert_chunks(chunks: list[ChunkIn]):
    if not chunks:
        return

    texts = [c.content for c in chunks]
    vectors = embed_batch(texts)

    with get_connection() as conn:
        with conn.cursor() as cur:
            for chunk, vector in zip(chunks, vectors):
                cur.execute(
                    """
                    INSERT INTO chunks (content, source, page, metadata, embedding)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        chunk.content,
                        chunk.source,
                        chunk.page,
                        json.dumps(chunk.metadata),
                        str(vector),  # pgvector accepts '[0.1,0.2,...]' text format
                    ),
                )
        conn.commit()

    print(f"Inserted {len(chunks)} chunks from this set.")


def load_all_chunk_sets():
    init_db()

    chunk_files = sorted(CHUNK_SETS_DIR.glob("*.json"))
    if not chunk_files:
        print(f"No chunk set files found in {CHUNK_SETS_DIR}")
        return

    for path in chunk_files:
        print(f"Loading {path.name}...")
        chunks = load_chunk_set(path)
        insert_chunks(chunks)

    print(f"Done. Loaded {len(chunk_files)} chunk set(s).")


if __name__ == "__main__":
    load_all_chunk_sets()