import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import service
from service import answer_question

UNANSWERABLE_QUESTIONS = [
    "What is the population of Mars?",
    "Who won the 2050 FIFA World Cup?",
    "What is my company's Q7 revenue?",
    "How do I bake a souffle using quantum computing?",
    "What is the CEO's home address?",
]


def test_five_refusals():
    """
    retrieve() is mocked to return no chunks -- the only condition
    check_refusal() actually triggers on -- so this test is deterministic
    and no longer depends on a live DB/retriever or LLM being reachable.
    """
    with patch.object(service, "retrieve", return_value=[]):
        for q in UNANSWERABLE_QUESTIONS:
            response = answer_question(q, conversation_id="test-refusal")
            assert response.refused is True, f"expected refusal for: {q}"
            assert response.citations == [], f"unexpected citations for: {q}"
            print(f"OK refused: {q}")


def test_happy_path_returns_citation():
    """
    Task 4's missing coverage: the core feature (an in-corpus question)
    had zero tests. This verifies an answerable question returns
    refused=False with a non-empty, correctly-formed citation list.

    retrieve() and chat() are both mocked so this doesn't touch a live
    DB or LLM. The fake chunk uses "content" (not "text") because
    prompt.py's build_prompt() reads c['content'] when assembling the
    context block. fake_answer stays a plain string, matching what
    chat() actually returns, and includes a "[1]" marker so
    extract_citations() resolves a citation back to the fake chunk --
    the same way it would with a real LLM response.
    """
    fake_chunks = [
        {"doc_name": "handbook.pdf", "page": 3, "content": "Password reset instructions..."},
    ]
    fake_answer = "To reset your password, go to Settings > Security. [1]"

    with patch.object(service, "retrieve", return_value=fake_chunks), \
         patch.object(service, "chat", return_value=fake_answer):
        response = answer_question("How do I reset my password?", conversation_id="test-happy")

    assert response.refused is False, "expected a real answer, got a refusal"
    assert len(response.citations) == 1, f"expected 1 citation, got {response.citations}"
    assert response.citations[0].doc_name == "handbook.pdf"
    assert response.citations[0].page == 3


if __name__ == "__main__":
    test_five_refusals()
    test_happy_path_returns_citation()
    print("All tests passed.")