import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from service import answer_question

UNANSWERABLE_QUESTIONS = [
    "What is the population of Mars?",
    "Who won the 2050 FIFA World Cup?",
    "What is my company's Q7 revenue?",
    "How do I bake a souffle using quantum computing?",
    "What is the CEO's home address?",
]


def test_five_refusals():
    for q in UNANSWERABLE_QUESTIONS:
        response = answer_question(q, conversation_id="test")
        assert response.refused is True, f"expected refusal for: {q}"
        assert response.citations == [], f"unexpected citations for: {q}"
        print(f"OK refused: {q}")


if __name__ == "__main__":
    test_five_refusals()
    print("All 5 refusals confirmed.")