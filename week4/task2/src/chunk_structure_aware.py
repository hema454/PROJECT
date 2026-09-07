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
    Returns a list of (heading_or_None, section_text, start_offset) tuples.
    start_offset is the position of the section's first character within
    `text` (the page text), tracked exactly while scanning line-by-line
    rather than recovered afterward via string search.

    Text appearing before the first detected heading gets heading=None
    -- this is the "lost their heading" / orphaned-text case.
    """
    lines = text.split("\n")
    sections = []
    current_heading = None
    current_lines = []
    current_start = 0
    pos = 0  # running character offset into `text`

    for line in lines:
        if is_heading(line):
            if current_lines:
                sections.append((current_heading, "\n".join(current_lines), current_start))
            current_heading = line.strip()
            current_lines = []
            current_start = pos + len(line) + 1  # right after this heading line + its "\n"
        else:
            if not current_lines:
                current_start = pos  # first line of this section starts here
            current_lines.append(line)
        pos += len(line) + 1  # +1 for the "\n" consumed by the earlier text.split("\n")

    if current_lines:
        sections.append((current_heading, "\n".join(current_lines), current_start))

    return sections


def main():
    data = load_json("loaded_documents.json")
    pages = data["pages"]

    all_chunks = []
    for page in pages:
        sections = split_into_sections(page["text"])
        chunk_idx = 0
        for heading, section_text, section_offset in sections:
            if not section_text.strip():
                continue
            if len(section_text) <= STRUCTURE_MAX_SECTION_SIZE:
                pieces = [(section_text, 0)]
            else:
                # Section too big -- fall back to recursive splitting
                # WITHIN this section only, per 4.5's "recursive" strategy.
                # recursive_split() returns offsets local to section_text,
                # so we add section_offset to get the true page offset.
                pieces = recursive_split(section_text, chunk_size=STRUCTURE_MAX_SECTION_SIZE)

            for piece_text, local_offset in pieces:
                all_chunks.append({
                    "chunk_id": f"{page['source']}_p{page['page_number']}_struct_{chunk_idx}",
                    "text": piece_text,
                    "source": page["source"],
                    "page_number": page["page_number"],
                    "char_offset_in_page": section_offset + local_offset,
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