import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from recall_eval import hit_at_k, normalize


def _chunk(content: str) -> dict:
    return {"content": content}


def test_hit_at_k_finds_gold_snippet_within_k():
    gold_snippet = "the mitochondria is the powerhouse of the cell"
    chunks = [
        _chunk("irrelevant chunk about something else entirely"),
        _chunk("another unrelated chunk of text here"),
        _chunk("The mitochondria is the powerhouse of the cell."),  # gold, position 3
        _chunk("yet another irrelevant chunk"),
        _chunk("one more irrelevant chunk"),
    ]

    # gold snippet sits at index 2 (rank 3) -- recall@3 should find it,
    # and recall@5 should too since it's a superset
    assert hit_at_k(gold_snippet, chunks, k=3) is True
    assert hit_at_k(gold_snippet, chunks, k=5) is True


def test_hit_at_k_misses_gold_snippet_outside_k():
    gold_snippet = "the mitochondria is the powerhouse of the cell"
    chunks = [
        _chunk("irrelevant chunk about something else entirely"),
        _chunk("another unrelated chunk of text here"),
        _chunk("yet another irrelevant chunk"),
        _chunk("one more irrelevant chunk"),
        _chunk("The mitochondria is the powerhouse of the cell."),  # gold, position 5
    ]

    # gold snippet only appears at rank 5 -- recall@3 must NOT find it,
    # recall@5 must find it
    assert hit_at_k(gold_snippet, chunks, k=3) is False
    assert hit_at_k(gold_snippet, chunks, k=5) is True


def test_hit_at_k_false_when_gold_snippet_absent_entirely():
    gold_snippet = "the mitochondria is the powerhouse of the cell"
    chunks = [
        _chunk("irrelevant chunk about something else entirely"),
        _chunk("another unrelated chunk of text here"),
        _chunk("yet another irrelevant chunk"),
    ]

    assert hit_at_k(gold_snippet, chunks, k=3) is False
    assert hit_at_k(gold_snippet, chunks, k=5) is False


def test_hit_at_k_matches_despite_whitespace_and_case_differences():
    # normalize() strips all whitespace and lowercases, to survive pypdf
    # dropping spaces at line-wrap boundaries -- confirm hit_at_k relies
    # on that and still matches under those conditions
    gold_snippet = "Simulating the  quantum   state"
    chunks = [_chunk("some text ...SIMULATINGTHEQUANTUMSTATE... more text")]

    assert hit_at_k(gold_snippet, chunks, k=1) is True


def test_normalize_collapses_whitespace_and_lowercases():
    assert normalize("Simulating the\nquantum   state") == "simulatingthequantumstate"


if __name__ == "__main__":
    test_hit_at_k_finds_gold_snippet_within_k()
    test_hit_at_k_misses_gold_snippet_outside_k()
    test_hit_at_k_false_when_gold_snippet_absent_entirely()
    test_hit_at_k_matches_despite_whitespace_and_case_differences()
    test_normalize_collapses_whitespace_and_lowercases()
    print("All hit_at_k tests passed.")