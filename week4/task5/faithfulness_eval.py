import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "task4"))

from embeddings import embed_text  # noqa: E402
from llm_client import chat  # noqa: E402

from db_variants import similarity_search_variant  # noqa: E402

JUDGE_PROMPT = (
    "You are checking whether an AI answer is fully supported by the given context. "
    "Reply with exactly 'SUPPORTED' if every claim in the answer appears in the context, "
    "or 'UNSUPPORTED: <the specific claim not found in context>' if any claim is not in the context."
)


def generate_answer(question: str, table_name: str, top_k: int = 5) -> tuple[str, str]:
    q_emb = embed_text(question)
    chunks = similarity_search_variant(table_name, q_emb, top_k)
    context = "\n\n".join(c["content"] for c in chunks)
    answer = chat(
        [
            {"role": "system", "content": "Answer the question using only the context provided."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ]
    )
    return answer, context


def judge_faithfulness(answer: str, context: str) -> str:
    return chat(
        [
            {"role": "system", "content": JUDGE_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nAnswer:\n{answer}"},
        ]
    )


def run(questions_path: str, table_name: str, out_path: str):
    questions = json.loads(Path(questions_path).read_text())
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["question", "answer", "verdict"])
        for q in questions:
            answer, context = generate_answer(q["question"], table_name)
            verdict = judge_faithfulness(answer, context)
            writer.writerow([q["question"], answer, verdict])
            print(f"{q['question'][:60]}... -> {verdict[:70]}")


if __name__ == "__main__":
    # pass the winning table name from recall_eval.py as the first argument
    table_name = sys.argv[1] if len(sys.argv) > 1 else "chunks_b"
    run("eval_questions.json", table_name, "faithfulness_results.csv")