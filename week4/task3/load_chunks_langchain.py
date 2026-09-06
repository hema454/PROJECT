"""
Loads the same chunk_sets JSON files as load_chunks.py, but into
LangChain's PGVector store instead of the raw `chunks` table -- so
search.py and search_langchain.py can be compared against equivalent data.

Run: python load_chunks_langchain.py
"""

import json
from pathlib import Path

from search_langchain import _vectorstore

CHUNK_SETS_DIR = Path(__file__).parent / "data" / "chunk_sets"


def load_all():
    chunk_files = sorted(CHUNK_SETS_DIR.glob("*.json"))
    if not chunk_files:
        print(f"No chunk set files found in {CHUNK_SETS_DIR}")
        return

    total = 0
    for path in chunk_files:
        raw = json.loads(path.read_text(encoding="utf-8"))
        texts = [item["content"] for item in raw]
        metadatas = [
            {"source": item["source"], "page": item.get("page"), **item.get("metadata", {})}
            for item in raw
        ]
        _vectorstore.add_texts(texts, metadatas=metadatas)
        print(f"Loaded {len(raw)} chunks from {path.name} into LangChain store.")
        total += len(raw)

    print(f"Done. Loaded {total} chunks total into LangChain's PGVector store.")


if __name__ == "__main__":
    load_all()