import json
import re
import sys
from pathlib import Path

# points at week4/ (the shared embeddings.py), not week4/task4 -- so this
# no longer breaks silently if task4 gets reorganized or renamed
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from embeddings import embed_text  # noqa: E402

from chunking_strategies import STRATEGIES  # noqa: E402
from db_variants import similarity_search_variant  # noqa: E402


def load_questions(path: str = "eval_questions.json") -> list[dict]:
    return json.loads(Path(path).read_text())


def normalize(text: str) -> str:
    # collapse and also strip all whitespace, since pypdf sometimes drops the
    # space at a line-wrap boundary (e.g. "simulating the" -> "simulatingthe")
    return re.sub(r"\s+", "", text).lower()


def hit_at_k(gold_snippet: str, chunks: list[dict], k: int) -> bool:
    gold = normalize(gold_snippet)
    for c in chunks[:k]:
        if gold in normalize(c["content"]):
            return True
    return False


def evaluate(questions: list[dict]) -> dict:
    results = {}
    for table_name in STRATEGIES:
        hits_3 = 0
        hits_5 = 0
        for q in questions:
            q_emb = embed_text(q["question"])
            chunks = similarity_search_variant(table_name, q_emb, 5)
            if hit_at_k(q["gold_snippet"], chunks, 3):
                hits_3 += 1
            if hit_at_k(q["gold_snippet"], chunks, 5):
                hits_5 += 1
        results[table_name] = {
            "recall@3": hits_3 / len(questions),
            "recall@5": hits_5 / len(questions),
        }
    return results


if __name__ == "__main__":
    questions = load_questions()
    results = evaluate(questions)
    for table_name, scores in results.items():
        print(f"{table_name}: recall@3={scores['recall@3']:.2f} recall@5={scores['recall@5']:.2f}")