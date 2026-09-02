import asyncio
import sys
from pathlib import Path
from typing import Callable

from golden_set import GOLDEN_SET, GoldenCase
from scorer import score_case

# Path to the folder containing the FastAPI service's service.py --
# adjust this if you move eval_suite relative to the service.
SERVICE_DIR = Path(__file__).resolve().parent.parent / "task2"
sys.path.insert(0, str(SERVICE_DIR))
import service  

ModelCall = Callable[[str, str], dict]


def run_eval(model_call: ModelCall, cases: list[GoldenCase] | None = None) -> tuple[int, int]:
    """Runs every golden case through model_call and returns (passed, total)."""
    cases = cases if cases is not None else GOLDEN_SET
    passed = 0
    for case in cases:
        actual = model_call(case.text, case.schema_description)
        if score_case(case, actual):
            passed += 1
    return passed, len(cases)


def _build_live_model_call() -> ModelCall:
    """Builds the model_call for scoring the current, live extraction
    prompt+model.
    """
    def _call(text: str, schema_description: str) -> dict:
        data, _repaired = asyncio.run(service.extract(text, schema_description))
        return data

    return _call


def main() -> None:
    model_call = _build_live_model_call()
    passed, total = run_eval(model_call)
    rate = passed / total * 100 if total else 0.0
    print(f"Pass rate: {passed}/{total} ({rate:.1f}%)")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()