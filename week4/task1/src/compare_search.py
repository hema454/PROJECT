"""
Step 3 (concepts 4.1-4.4): Find one query where semantic search clearly
beats keyword search, and one where keyword search would have won.

EVALUATION CRITERIA (stated explicitly, not left implied):
Each test case has a fixed query AND a known "expected match" -- the
specific sentence from the corpus that is the objectively correct
answer to that query. For each method (semantic, keyword) we check:
    did that method's TOP-1 result equal the expected match?  (True/False)

CASE A is fixed, taken directly from the real Step 2 results
(nearest_neighbors_results.md): query "How can I make my app load
faster?" -> top match "Why is the dashboard loading slowly?" (score
0.5659), with zero shared content words between query and match.

CASE B tests several candidate exact-identifier queries in one run
(rather than guessing one at a time) to find a real case where keyword
search's top-1 is correct but semantic search's top-1 is not.

Run: python src/compare_search.py
Requires outputs/embeddings.npy and outputs/sentences.txt
(run src/embed_corpus.py first).

Output: outputs/search_comparison_results.md
"""

import os
import re
from sentence_transformers import SentenceTransformer, util

from config import MODEL_NAME, TOP_K
from utils import OUT_DIR, create_output_dir, load_embedded_corpus

CASE_A = {
    "title": "Case A: where semantic search wins",
    "query": "How can I make my app load faster?",
    "expected_match": "Why is the dashboard loading slowly?",
    "why": "Verified from Step 2 (nearest_neighbors_results.md): this was the "
           "real top-1 semantic match, similarity 0.5659, with zero shared "
           "content words between query and match ('load'/'faster' vs "
           "'loading'/'slowly' -- not even the same literal tokens).",
}

# Several candidate exact identifiers to test for Case B in one run.
CASE_B_CANDIDATES = [
    {
        "query": "TXN-88214",
        "expected_match": "Transaction TXN-88214 failed due to an expired card.",
    },
    {
        "query": "TXN-88215",
        "expected_match": "Transaction TXN-88215 failed due to an expired card.",
    },
]

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "am", "be", "been",
    "how", "what", "when", "where", "why", "who", "which",
    "do", "does", "did", "can", "could", "will", "would", "should",
    "i", "my", "me", "you", "your", "it", "its", "this", "that",
    "to", "of", "in", "on", "at", "for", "with", "and", "or", "if",
    "get", "got",
}


def tokenize(text: str):
    tokens = set(re.findall(r"[a-z0-9\-]+", text.lower()))
    return tokens - STOPWORDS


def keyword_search(query: str, sentences: list, k=TOP_K):
    """
    Keyword search: score = number of shared CONTENT words (stopwords
    removed) between query and sentence, plus an exact substring bonus
    so identifiers/codes are rewarded for a literal match.
    """
    query_tokens = tokenize(query)
    scored = []
    for sent in sentences:
        sent_tokens = tokenize(sent)
        overlap = len(query_tokens & sent_tokens)
        substring_bonus = 5 if query.lower() in sent.lower() else 0
        scored.append((sent, overlap + substring_bonus))
    scored.sort(key=lambda x: -x[1])
    return scored[:k]


def semantic_search(model, query: str, sentences: list, corpus_vecs, k=TOP_K):
    query_vec = model.encode(query, convert_to_numpy=True)
    hits = util.semantic_search(query_vec, corpus_vecs, top_k=k)[0]
    return [(sentences[hit["corpus_id"]], float(hit["score"])) for hit in hits]


def run_case(title, query, expected, model, sentences, embeddings, lines, why=None):
    kw_results = keyword_search(query, sentences)
    sem_results = semantic_search(model, query, sentences, embeddings)

    kw_pass = kw_results[0][0] == expected
    sem_pass = sem_results[0][0] == expected

    print(f"\n{title}")
    print(f"Query: {query}")
    print(f"Expected match: {expected}")
    print(f"  Keyword  top-1 == expected: {kw_pass}  ({kw_results[0][0]})")
    print(f"  Semantic top-1 == expected: {sem_pass}  ({sem_results[0][0]}, score {sem_results[0][1]:.4f})")

    lines.append(f"## {title}\n")
    lines.append(f"**Query:** \"{query}\"")
    lines.append(f"**Expected match:** \"{expected}\"")
    if why:
        lines.append(f"**Why:** {why}\n")
    lines.append(f"**Keyword top-1 == expected: {kw_pass}**")
    for sent, score in kw_results:
        marker = " <- expected" if sent == expected else ""
        lines.append(f"- ({score}) {sent}{marker}")
    lines.append(f"\n**Semantic top-1 == expected: {sem_pass}**")
    for sent, score in sem_results:
        marker = " <- expected" if sent == expected else ""
        lines.append(f"- ({score:.4f}) {sent}{marker}")
    lines.append("")

    return kw_pass, sem_pass


def main():
    create_output_dir()
    embeddings, sentences = load_embedded_corpus()
    model = SentenceTransformer(MODEL_NAME)

    lines = [
        "# Semantic Search vs Keyword Search (Step 3)\n",
        "**What this measures:** for each case, whether each method's "
        "top-1 result equals the known expected match (pass/fail).\n",
    ]

    summary_rows = []

    # --- Case A (fixed, already verified) ---
    kw_pass, sem_pass = run_case(
        CASE_A["title"], CASE_A["query"], CASE_A["expected_match"],
        model, sentences, embeddings, lines, why=CASE_A["why"],
    )
    summary_rows.append((CASE_A["title"], kw_pass, sem_pass))

    # --- Case B candidates (testing several to find a genuine keyword-win) ---
    lines.append("## Case B candidates: where keyword search should win\n")
    best_case_b = None
    for i, cand in enumerate(CASE_B_CANDIDATES, 1):
        kw_pass, sem_pass = run_case(
            f"Case B candidate {i}", cand["query"], cand["expected_match"],
            model, sentences, embeddings, lines,
        )
        summary_rows.append((f"Case B candidate {i}: \"{cand['query']}\"", kw_pass, sem_pass))
        if kw_pass and not sem_pass and best_case_b is None:
            best_case_b = cand["query"]

    lines.append("## Summary\n")
    lines.append("| Case | Keyword top-1 correct | Semantic top-1 correct |")
    lines.append("|---|---|---|")
    for title, kw_pass, sem_pass in summary_rows:
        lines.append(f"| {title} | {kw_pass} | {sem_pass} |")

    out_path = os.path.join(OUT_DIR, "search_comparison_results.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nSaved full results to {out_path}")

    if best_case_b:
        print(f"\n*** Found a genuine keyword-wins case: \"{best_case_b}\" ***")
        print("Use this one as your official Case B in ANALYSIS.md.")
    else:
        print(
            "\nNone of the Case B candidates showed keyword-pass/semantic-fail "
            "in this run. Add another rare identifier from data/corpus.txt to "
            "CASE_B_CANDIDATES in this script and re-run."
        )


if __name__ == "__main__":
    main()