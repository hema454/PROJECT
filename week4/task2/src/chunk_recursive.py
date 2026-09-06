"""
Step 2b (concepts 4.5, 4.6, 4.7, 4.10): Recursive chunking.

Tries to split on the "biggest" natural boundary first, and only falls
back to a smaller one if a piece is still too big:
  paragraph breaks ("\n\n") -> line breaks ("\n") -> sentence ends
  (". ") -> word boundaries (" ") -> raw character cut (last resort)

This is a from-scratch reimplementation of the same idea as LangChain's
RecursiveCharacterTextSplitter (4.10) -- written directly so this
project has no hard dependency on langchain being installed. If
langchain IS available in your environment, you can swap this for:

    from langchain.text_splitter import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_text(text)

Run: python src/chunk_recursive.py
Requires outputs/loaded_documents.json (run src/load_documents.py first).
Output: outputs/chunks_recursive.json
"""

from config import CHUNK_SIZE, CHUNK_OVERLAP
from utils import load_json, save_json

SEPARATORS = ["\n\n", "\n", ". ", " ", ""]  # tried in this order, biggest first


def _split_on_separator(text, separator):
    if separator == "":
        return list(text)  # last resort: individual characters
    parts = text.split(separator)
    # put the separator back (except after the final piece) so meaning/
    # punctuation isn't silently dropped
    return [p + separator if i < len(parts) - 1 else p for i, p in enumerate(parts)]


def _merge_pieces(pieces, chunk_size, overlap):
    """Greedily merge small pieces into chunks up to chunk_size, with overlap."""
    chunks = []
    current = ""
    for piece in pieces:
        if len(current) + len(piece) <= chunk_size:
            current += piece
        else:
            if current.strip():
                chunks.append(current)
            # start next chunk with overlap from the end of the previous one
            overlap_text = current[-overlap:] if overlap > 0 else ""
            current = overlap_text + piece
    if current.strip():
        chunks.append(current)
    return chunks


def recursive_split(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP, separators=None):
    """
    Recursively splits `text` using the first separator that actually
    breaks it into pieces small enough to work with, falling back to
    the next separator in the list for any piece still too large.
    """
    if separators is None:
        separators = SEPARATORS
    if not text.strip():
        return []
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    separator, remaining_separators = separators[0], separators[1:]
    pieces = _split_on_separator(text, separator)

    # Any individual piece still too big gets recursively split further
    # with the NEXT separator down the list (paragraph -> line -> sentence -> word -> char).
    expanded = []
    for piece in pieces:
        if len(piece) > chunk_size and remaining_separators:
            expanded.extend(recursive_split(piece, chunk_size, overlap, remaining_separators))
        else:
            expanded.append(piece)

    return _merge_pieces(expanded, chunk_size, overlap)


def main():
    data = load_json("loaded_documents.json")
    pages = data["pages"]

    all_chunks = []
    for page in pages:
        chunks = recursive_split(page["text"])
        for i, chunk_text in enumerate(chunks):
            all_chunks.append({
                "chunk_id": f"{page['source']}_p{page['page_number']}_recursive_{i}",
                "text": chunk_text,
                "source": page["source"],
                "page_number": page["page_number"],
                "strategy": "recursive",
            })

    out_path = save_json(all_chunks, "chunks_recursive.json")
    print(f"Recursive chunking: {len(all_chunks)} chunks saved to {out_path}")


if __name__ == "__main__":
    main()