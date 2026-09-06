import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "task4"))

from embeddings import embed_text  # noqa: E402

from db_variants import similarity_search_variant  # noqa: E402


def find_rank(question: str, gold_snippet: str, table_name: str = "chunks_b", top_k: int = 30):
    q_emb = embed_text(question)
    rows = similarity_search_variant(table_name, q_emb, top_k)
    gold = gold_snippet.replace(" ", "").lower()
    for i, r in enumerate(rows, 1):
        content = r["content"].replace(" ", "").replace("\n", "").lower()
        if gold in content:
            print(f"Found at rank {i} (distance={r['distance']:.4f})")
            print(f"  content: {r['content'][:300]!r}")
            return
    print(f"NOT found in top {top_k}")


if __name__ == "__main__":
    find_rank(
        "How long is customer data retained after account closure?",
        "typically ninety days after account closure",
    )