"""
Step 2c (concepts 4.5, 4.6, 4.10): Structure-aware chunking.

Splits primarily on detected HEADINGS (using the heuristics in
config.HEADING_PATTERNS), so each chunk is naturally "one section" of
the document. Only falls back to recursive_split() (4.10's size-based
splitting) when a single section is still bigger than
STRUCTURE_MAX_SECTION_SIZE.

Unlike chunk_fixed.py and chunk_recursive.py, each chunk here also
carries a `section` field -- the heading it fell under, or None if the
text appeared before any detected heading (this "orphaned" case is
exactly one of the failure modes Step 3 asks you to look for).

Run: python src/chunk_structure_aware.py
Requires outputs/loaded_documents.json (run src/load_documents.py first).
Output: outputs/chunks_structure_aware.json
"""

from config import HEADING_PATTERNS, MIN_HEADING_LEN, MAX_HEADING_LEN, STRUCTURE_MAX_SECTION_SIZE
from chunk_recursive import recursive_split
from utils import load_json, save_json


def is_heading(line: str) -> bool:
    line = line.strip()
    if not (MIN_HEADING_LEN <= len(line) <= MAX_HEADING_LEN):
        return False
    if line.endswith((".", ",", ";", ":")):
        return False  # sentences end in punctuation; headings usually don't
    return any(pattern.match(line) for pattern in HEADING_PATTERNS)


def split_into_sections(text: str):
    """
    Returns a list of (heading_or_None, section_text) tuples.
    Text appearing before the first detected heading gets heading=None
    -- this is the "lost their heading" / orphaned-text case.
    """
    lines = text.split("\n")
    sections = []
    current_heading = None
    current_lines = []

    for line in lines:
        if is_heading(line):
            if current_lines:
                sections.append((current_heading, "\n".join(current_lines)))
            current_heading = line.strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_heading, "\n".join(current_lines)))

    return sections


def main():
    data = load_json("loaded_documents.json")
    pages = data["pages"]

    all_chunks = []
    for page in pages:
        sections = split_into_sections(page["text"])
        chunk_idx = 0
        for heading, section_text in sections:
            if not section_text.strip():
                continue
            if len(section_text) <= STRUCTURE_MAX_SECTION_SIZE:
                pieces = [section_text]
            else:
                # Section too big -- fall back to recursive splitting
                # WITHIN this section only, per 4.5's "recursive" strategy.
                pieces = recursive_split(section_text, chunk_size=STRUCTURE_MAX_SECTION_SIZE)

            for piece in pieces:
                all_chunks.append({
                    "chunk_id": f"{page['source']}_p{page['page_number']}_struct_{chunk_idx}",
                    "text": piece,
                    "source": page["source"],
                    "page_number": page["page_number"],
                    "section": heading,  # None if this text had no detected heading above it
                    "strategy": "structure_aware",
                })
                chunk_idx += 1

    out_path = save_json(all_chunks, "chunks_structure_aware.json")
    n_orphaned = sum(1 for c in all_chunks if c["section"] is None)
    print(f"Structure-aware chunking: {len(all_chunks)} chunks saved to {out_path}")
    print(f"  {n_orphaned} chunk(s) had no detected heading above them (section=None)")


if __name__ == "__main__":
    main()