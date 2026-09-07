"""
Step 4 (concept 4.8): Attach metadata to every chunk: source, page,
section, and date.

Reads all three chunk sets (already carrying source/page from Step 2)
and normalizes them to a common metadata shape, adding:
  - section: heading, if known (only structure_aware chunks have this
    natively; fixed/recursive get section=None since those strategies
    don't track headings)
  - date: the ingestion date recorded in loaded_documents.json

Run: python src/attach_metadata.py
Requires all three outputs/chunks_*.json files to already exist.
Output: outputs/chunks_fixed_final.json, chunks_recursive_final.json,
        chunks_structure_aware_final.json
"""

from utils import load_json, save_json

CHUNK_FILES = {
    "fixed": "chunks_fixed.json",
    "recursive": "chunks_recursive.json",
    "structure_aware": "chunks_structure_aware.json",
}


def attach_metadata(chunks, ingested_date):
    for chunk in chunks:
        # NOTE: `source` and `page` are intentionally duplicated here even
        # though they already exist at the top level of `chunk`. This is a
        # deliberate design choice, not an oversight: the `metadata` dict
        # is the self-contained payload that gets sent downstream (e.g. to
        # the vector DB alongside the embedding). Consumers that only see
        # `metadata` -- not the full chunk record -- still need source/page
        # available without reaching back into the parent object.
        chunk["metadata"] = {
            "source": chunk["source"],
            "page": chunk["page_number"],
            "section": chunk.get("section"),  # already set for structure_aware; None otherwise
            "date": ingested_date,
        }
    return chunks


def main():
    loaded = load_json("loaded_documents.json")
    ingested_date = loaded["ingested_date"]

    for strategy, filename in CHUNK_FILES.items():
        chunks = load_json(filename)
        chunks = attach_metadata(chunks, ingested_date)
        out_name = filename.replace(".json", "_final.json")
        out_path = save_json(chunks, out_name)
        print(f"{strategy}: {len(chunks)} chunks, metadata attached -> {out_path}")


if __name__ == "__main__":
    main()