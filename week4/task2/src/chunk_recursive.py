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


def _piece_offsets(pieces):
    """
    Given pieces that concatenate back to the original text exactly (which
    _split_on_separator guarantees), return each piece's start offset,
    relative to the start of that original text.
    """
    offsets = []
    pos = 0
    for p in pieces:
        offsets.append(pos)
        pos += len(p)
    return offsets


def _merge_pieces(pieces, piece_offsets, chunk_size, overlap):
    """
    Greedily merge small pieces into chunks up to chunk_size, with overlap.

    Returns a list of (chunk_text, start_offset) tuples. start_offset is in
    the same coordinate system as piece_offsets (the caller's `text`), and
    is tracked exactly rather than recovered later via string search:
    a normal chunk's start is just its first piece's offset, and an
    overlap-continued chunk's start is computed from the END of the
    previous chunk minus the overlap length, since the overlap text is
    literally the tail of that previous chunk.
    """
    chunks = []
    current = ""
    current_start = None
    for piece, offset in zip(pieces, piece_offsets):
        if current_start is None:
            current_start = offset
        if len(current) + len(piece) <= chunk_size:
            current += piece
        else:
            if current.strip():
                chunks.append((current, current_start))
            overlap_text = current[-overlap:] if overlap > 0 else ""
            prev_end = current_start + len(current)
            overlap_start = prev_end - len(overlap_text)
            current = overlap_text + piece
            current_start = overlap_start
    if current.strip():
        chunks.append((current, current_start))
    return chunks


def recursive_split(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP, separators=None):
    """
    Recursively splits `text` using the first separator that actually
    breaks it into pieces small enough to work with, falling back to
    the next separator in the list for any piece still too large.

    Returns a list of (chunk_text, start_offset) tuples, where
    start_offset is relative to the start of `text` as passed into THIS
    call. At the top-level call site (a whole page's text), that means
    start_offset is directly the offset within the page -- no separate
    re-location step needed.
    """
    if separators is None:
        separators = SEPARATORS
    if not text.strip():
        return []
    if len(text) <= chunk_size:
        return [(text, 0)] if text.strip() else []

    separator, remaining_separators = separators[0], separators[1:]
    pieces = _split_on_separator(text, separator)
    piece_offsets = _piece_offsets(pieces)  # local to `text`, 0-based

    # Any individual piece still too big gets recursively split further
    # with the NEXT separator down the list (paragraph -> line -> sentence -> word -> char).
    expanded = []  # list of (piece_text, offset_local_to_text)
    for piece, offset in zip(pieces, piece_offsets):
        if len(piece) > chunk_size and remaining_separators:
            sub_chunks = recursive_split(piece, chunk_size, overlap, remaining_separators)
            # sub_chunks' offsets are local to `piece`; shift so they're
            # local to `text` instead, by adding piece's own offset in `text`
            expanded.extend((sub_text, offset + sub_offset) for sub_text, sub_offset in sub_chunks)
        else:
            expanded.append((piece, offset))

    ex_texts = [t for t, _ in expanded]
    ex_offsets = [o for _, o in expanded]
    return _merge_pieces(ex_texts, ex_offsets, chunk_size, overlap)


def main():
    data = load_json("loaded_documents.json")
    pages = data["pages"]

    all_chunks = []
    for page in pages:
        chunks = recursive_split(page["text"])
        for i, (chunk_text, offset) in enumerate(chunks):
            all_chunks.append({
                "chunk_id": f"{page['source']}_p{page['page_number']}_recursive_{i}",
                "text": chunk_text,
                "source": page["source"],
                "page_number": page["page_number"],
                "char_offset_in_page": offset,
                "strategy": "recursive",
            })

    out_path = save_json(all_chunks, "chunks_recursive.json")
    print(f"Recursive chunking: {len(all_chunks)} chunks saved to {out_path}")


if __name__ == "__main__":
    main()