"""
Step 2a (concepts 4.5, 4.6, 4.7): Fixed-size chunking.

Cuts every CHUNK_SIZE characters, regardless of sentence/word boundaries,
with CHUNK_OVERLAP characters repeated between consecutive chunks. This
is the "blind ruler cut" strategy -- included deliberately so Step 3's
manual review has real mid-sentence-split chunks to find.

Run: python src/chunk_fixed.py
Requires outputs/loaded_documents.json (run src/load_documents.py first).
Output: outputs/chunks_fixed.json
"""

from config import CHUNK_SIZE, CHUNK_OVERLAP
from utils import load_json, save_json


def fixed_size_chunks(text: str, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """
    Pure character-count chunking. No awareness of words, sentences, or
    structure -- cuts wherever the count lands. Returns a list of
    (chunk_text, start_offset) tuples; start_offset is the character
    index into `text` where this chunk begins (kept for traceability).
    """
    if not text.strip():
        return []

    chunks = []
    start = 0
    step = max(chunk_size - overlap, 1)  # guard against overlap >= chunk_size
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end]
        if chunk_text.strip():
            chunks.append((chunk_text, start))
        start += step
    return chunks


def main():
    data = load_json("loaded_documents.json")
    pages = data["pages"]

    all_chunks = []
    for page in pages:
        chunks = fixed_size_chunks(page["text"])
        for i, (chunk_text, offset) in enumerate(chunks):
            all_chunks.append({
                "chunk_id": f"{page['source']}_p{page['page_number']}_fixed_{i}",
                "text": chunk_text,
                "source": page["source"],
                "page_number": page["page_number"],
                "char_offset_in_page": offset,
                "strategy": "fixed",
            })

    out_path = save_json(all_chunks, "chunks_fixed.json")
    print(f"Fixed-size chunking: {len(all_chunks)} chunks saved to {out_path}")


if __name__ == "__main__":
    main()