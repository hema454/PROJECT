"""
Step 3 helper (not a chunking concept itself -- just tooling): pulls a
sample of 50 chunks across all three strategies into one readable file,
so you can actually read them by hand and note failures, instead of
digging through three separate JSON files.

This script does NOT do the manual review for you -- Step 3 explicitly
requires reading them yourself. It only assembles the reading material
and a findings template to fill in.

Run: python src/sample_for_review.py
Requires outputs/chunks_*_final.json (run attach_metadata.py first).
Output:
  outputs/review_sample.md   -> 50 chunks to read, ~17 from each strategy
  outputs/manual_review.md   -> template for your findings (Step 3 + Step 4 "done when")
"""

import os
from utils import load_json, save_json, OUT_DIR, create_output_dir

SAMPLE_TOTAL = 50


def main():
    create_output_dir()

    sets = {
        "fixed": load_json("chunks_fixed_final.json"),
        "recursive": load_json("chunks_recursive_final.json"),
        "structure_aware": load_json("chunks_structure_aware_final.json"),
    }

    per_strategy = SAMPLE_TOTAL // len(sets)
    lines = ["# Chunk Review Sample (Step 3)\n", f"{SAMPLE_TOTAL} chunks, ~{per_strategy} per strategy.\n"]

    n = 0
    for strategy, chunks in sets.items():
        take = chunks[:per_strategy] if len(chunks) >= per_strategy else chunks
        lines.append(f"\n## Strategy: {strategy} ({len(take)} chunks shown)\n")
        for chunk in take:
            n += 1
            meta = chunk["metadata"]
            lines.append(f"### [{n}] {chunk['chunk_id']}")
            lines.append(
                f"source={meta['source']} | page={meta['page']} | "
                f"section={meta['section']} | date={meta['date']}"
            )
            lines.append("```")
            lines.append(chunk["text"])
            lines.append("```\n")

    review_path = os.path.join(OUT_DIR, "review_sample.md")
    with open(review_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {n} chunks to review in {review_path}")

    # Findings template -- Step 3 + the exercise's "done when" criterion
    template = """# Manual Review Findings (Step 3)

Read outputs/review_sample.md, then fill this in.

## Mid-sentence splits found
(chunk_id, and the sentence it cut through)
-

## Pure "page furniture" found
(chunk_id, and what it is -- header/footer/page number/boilerplate)
-

## Chunks that lost their heading
(chunk_id where section=None but the text clearly belongs under a heading)
-

## "Done when" -- three specific useless chunks, and why

1. chunk_id: ...
   Why it's useless: ...

2. chunk_id: ...
   Why it's useless: ...

3. chunk_id: ...
   Why it's useless: ...
"""
    findings_path = os.path.join(OUT_DIR, "manual_review.md")
    with open(findings_path, "w", encoding="utf-8") as f:
        f.write(template)
    print(f"Findings template ready at {findings_path}")


if __name__ == "__main__":
    main()