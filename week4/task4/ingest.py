import sys
from pathlib import Path

# points at week4/ (the shared embeddings.py), not the old local task4/embeddings.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pypdf import PdfReader

from db import init_db, insert_chunk
from embeddings import embed_text

CHUNK_SIZE = 800
OVERLAP = 100


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + size])
        start += size - overlap
    return chunks


def ingest_pdf(path: Path):
    reader = PdfReader(str(path))
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for chunk in chunk_text(text):
            if chunk.strip():
                insert_chunk(path.name, page_num, chunk, embed_text(chunk))


def ingest_txt(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    for chunk in chunk_text(text):
        if chunk.strip():
            insert_chunk(path.name, 1, chunk, embed_text(chunk))


def main(corpus_dir: str):
    init_db()
    for path in Path(corpus_dir).glob("*"):
        if path.suffix.lower() == ".pdf":
            ingest_pdf(path)
        elif path.suffix.lower() == ".txt":
            ingest_txt(path)
        else:
            continue
        print(f"ingested {path.name}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "corpus")