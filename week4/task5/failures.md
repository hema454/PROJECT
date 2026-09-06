# Retrieval failures

Three specific failures from this system, named by cause rather than symptom.

## Failure 1: Zero chunks for an entire document

- **Question:** "How long did Engineering estimate the billing dashboard work would take?"
- **What was retrieved:** Nothing relevant — the model correctly reported no information found, rather than guessing.
- **What should have been retrieved:** The sentence "Engineering estimated six weeks for the billing work" from `meeting_notes_scanned.pdf`.
- **Cause:** `meeting_notes_scanned.pdf` is an image-based PDF with no embedded text layer. `pypdf.extract_text()` silently returns an empty string for every page, so `ingest_variants.py` produces zero chunks for this document even though it logs "ingested" for it regardless. This affected all 3 questions written against this document (15% of the labeled set) across every chunking strategy — it's an ingestion-layer failure, not a chunking or retrieval-ranking problem, and no amount of threshold or top-k tuning would fix it. Requires OCR (e.g. `pytesseract`) before this document can be chunked at all.

## Failure 2: Context conflation from topically-overlapping chunks

- **Question:** "What must a new engineer complete before joining the on-call rotation?"
- **What was retrieved:** The correct chunk (Section 4, "On-Call Rotation" — incident response training + shadowing two live incidents), plus a second chunk from Section 20 ("Onboarding for New Engineers" — a separate two-week onboarding program that also ends in a shadow on-call shift).
- **What should have been retrieved:** Just the Section 4 chunk; Section 20 answers a related but distinct question.
- **Cause:** The two sections use overlapping vocabulary ("on-call", "shadow", "new engineer") despite describing different policies, so both scored close enough in cosine similarity to both land in the top-k. The generator then synthesized a claim asserting these are "separate requirements," which the source text doesn't actually state that way — an inaccuracy introduced by feeding it two adjacent-but-distinct passages together rather than a single unambiguous one. This is a retrieval-precision failure: recall was fine (the right chunk was found), but the extra chunk pulled alongside it degraded faithfulness.

## Failure 3: Chunk boundaries splitting answers under fixed-size chunking

- **Question set:** General pattern observed across the `chunks_a` strategy (fixed 300 characters, no overlap) during the recall comparison.
- **What was retrieved:** `chunks_a` scored recall@3 = 0.70, meaningfully below `chunks_c`'s 0.85, on the same 20 questions and same source documents.
- **What should have been retrieved:** The same rate as `chunks_c`, since the underlying text is identical.
- **Cause:** At 300 characters with zero overlap, `chunks_a` regularly cuts a sentence in half exactly at a chunk boundary — an answer-bearing sentence spanning the ~300-char cutoff gets split so that neither resulting chunk contains the complete phrase needed to answer the question. Because there's no overlap, that lost text isn't recovered by an adjacent chunk either. `chunks_c`'s sentence-aligned windows never split mid-sentence, which is the direct explanation for its higher recall on the same corpus.