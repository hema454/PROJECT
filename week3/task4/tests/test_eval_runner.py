import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval_runner import run_eval
from golden_set import GOLDEN_SET, GoldenCase
from scorer import score_case


def test_golden_set_has_at_least_25_cases_with_at_least_3_refusals():
    assert len(GOLDEN_SET) >= 25
    refusal_count = sum(1 for case in GOLDEN_SET if case.is_refusal)
    assert refusal_count >= 3


def test_score_case_passes_on_normalized_match():
    case = GoldenCase("t1", "text", "total", {"total": "$312.50"})
    # normalization strips the currency symbol -- "312.50" should still match
    assert score_case(case, {"total": "312.50"}) is True


def test_score_case_fails_on_mismatch():
    case = GoldenCase("t2", "text", "invoice_number", {"invoice_number": "4821"})
    assert score_case(case, {"invoice_number": "9999"}) is False


def test_run_eval_computes_pass_rate_with_mocked_model_call():
    cases = [
        GoldenCase("a", "t", "f", {"f": "x"}),
        GoldenCase("b", "t", "f", {"f": "y"}),
        GoldenCase("refuse", "t", "f", {"f": None}, is_refusal=True),
    ]

    def fake_model_call(text: str, schema_description: str) -> dict:
        # Always returns "x" and never leaves fields empty --
        # passes case "a", fails case "b", fails the refusal case.
        return {"f": "x"}

    passed, total = run_eval(fake_model_call, cases=cases)
    assert (passed, total) == (1, 3)