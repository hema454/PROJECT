"""
Step 2 (concepts 4.1-4.4): For 5 queries, find the nearest neighbours
by hand with numpy, then confirm the same result through the library.

WHAT "COMPARISON" MEANS HERE (stated explicitly, not left implied):
This script checks CORRECTNESS ONLY -- does the manual numpy
implementation return the exact same top-K sentences, in the same
order, as the library function? It does NOT compare speed/performance;
a wall-clock timing is printed for interest but is not the pass/fail
criterion. The result recorded for each query is a boolean:
"manual and library top-K match: True/False".

Run: python src/nearest_neighbors.py
Requires outputs/embeddings.npy and outputs/sentences.txt
(run src/embed_corpus.py first).

Output: outputs/nearest_neighbors_results.md
"""

import os
import time
import numpy as np
from sentence_transformers import SentenceTransformer, util

from config import MODEL_NAME, TOP_K
from utils import OUT_DIR, create_output_dir, load_embedded_corpus

QUERIES = [
    "How do I get my money back?",
    "My account got locked, what do I do?",
    "What happens if I go over the API rate limit?",
    "How can I make my app load faster?",
    "Is my information safe with you?",
]


def cosine_similarity_manual(query_vec: np.ndarray, corpus_vecs: np.ndarray) -> np.ndarray:
    dot_products = corpus_vecs @ query_vec
    query_norm = np.linalg.norm(query_vec)
    corpus_norms = np.linalg.norm(corpus_vecs, axis=1)
    similarities = dot_products / (corpus_norms * query_norm)
    return similarities


def top_k_manual(query_vec: np.ndarray, corpus_vecs: np.ndarray, sentences: list, k=TOP_K):
    sims = cosine_similarity_manual(query_vec, corpus_vecs)
    top_idx = np.argsort(-sims)[:k]
    return [(sentences[i], float(sims[i])) for i in top_idx]


def top_k_library(query_vec: np.ndarray, sentences: list, corpus_vecs: np.ndarray, k=TOP_K):
    hits = util.semantic_search(query_vec, corpus_vecs, top_k=k)[0]
    return [(sentences[hit["corpus_id"]], float(hit["score"])) for hit in hits]


def main():
    create_output_dir()
    embeddings, sentences = load_embedded_corpus()
    print(f"Loaded {len(sentences)} sentences, embeddings shape {embeddings.shape}")

    model = SentenceTransformer(MODEL_NAME)

    report_lines = [
        "# Nearest Neighbours: Manual numpy vs Library (Step 2)\n",
        "**What this measures:** whether the manual numpy cosine-similarity "
        "implementation and the sentence-transformers library function agree "
        "on the same top-{} sentences for each query (correctness check, not "
        "a speed comparison). Timing is included for reference only.\n".format(TOP_K),
    ]

    all_match = True

    for query in QUERIES:
        query_vec = model.encode(query, convert_to_numpy=True)

        t0 = time.perf_counter()
        manual_results = top_k_manual(query_vec, embeddings, sentences)
        t_manual = time.perf_counter() - t0

        t0 = time.perf_counter()
        library_results = top_k_library(query_vec, sentences, embeddings)
        t_library = time.perf_counter() - t0

        manual_top_sentences = [s for s, _ in manual_results]
        library_top_sentences = [s for s, _ in library_results]
        match = manual_top_sentences == library_top_sentences
        all_match = all_match and match

        print(f"\nQuery: {query}")
        print(f"  Manual == Library top-{TOP_K} match: {match}")
        print(f"  Timing (reference only) -- manual: {t_manual*1000:.2f}ms, library: {t_library*1000:.2f}ms")

        report_lines.append(f"## Query: \"{query}\"\n")
        report_lines.append(f"**Correctness check (manual == library top-{TOP_K}):** {match}")
        report_lines.append(
            f"**Timing (reference only, not the pass/fail criterion):** "
            f"manual {t_manual*1000:.2f}ms, library {t_library*1000:.2f}ms\n"
        )
        report_lines.append("| Rank | Manual (numpy) | Score | Library | Score |")
        report_lines.append("|---|---|---|---|---|")
        for rank in range(TOP_K):
            m_sent, m_score = manual_results[rank]
            l_sent, l_score = library_results[rank]
            report_lines.append(
                f"| {rank+1} | {m_sent} | {m_score:.4f} | {l_sent} | {l_score:.4f} |"
            )
        report_lines.append("")

    report_lines.append(f"## Summary\n")
    report_lines.append(f"All {len(QUERIES)} queries matched between manual and library: **{all_match}**")

    out_path = os.path.join(OUT_DIR, "nearest_neighbors_results.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"\nSaved full results to {out_path}")
    print(f"All queries matched: {all_match}")


if __name__ == "__main__":
    main()