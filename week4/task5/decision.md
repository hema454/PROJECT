# Chunking strategy decision

## Recall results

| Strategy | Description | recall@3 | recall@5 |
|---|---|---|---|
| chunks_a | fixed 300 chars, no overlap | 0.70 | 0.70 |
| chunks_b | fixed 800 chars, 100 overlap | 0.75 | 0.85 |
| chunks_c | sentence-window, 3 sentences/chunk | 0.85 | 0.85 |

## Winner

**Chosen strategy:** chunks_c (sentence-window, 3 sentences/chunk)

**Why:** chunks_c has the best recall@3 of all three strategies (0.85), matching chunks_b's
recall@5 but reaching it two positions sooner. chunks_a is clearly worst (0.70 at both k=3
and k=5) — fixed 300-char chunks with no overlap are too small and lose surrounding context,
frequently splitting the answer away from the sentence that states it. chunks_b closes most
of that gap with a larger window and overlap, but chunks_c's sentence-aligned boundaries
retrieve the correct answer more reliably at a shallower depth, which matters directly for
a top-k=3/5 retrieval system: fewer irrelevant chunks reach the LLM's context window.

## Cleanup

- [x] Dropped the two losing tables: `chunks_a`, `chunks_b` via `drop_losers.py`.
- [x] Confirmed only the winning table (`chunks_c`) remains.