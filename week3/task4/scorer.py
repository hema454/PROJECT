import re

from golden_set import GoldenCase


def _normalize(value) -> str:
    """Loose comparison: strips currency symbols/commas/case, and treats
    numeric values by their numeric value so "312.50" == 312.5 == "312.5".
    """
    if value is None:
        return ""
    s = str(value).strip().lower()
    s = re.sub(r"[^\w.]+", "", s)
    try:
        return f"{float(s):g}"
    except ValueError:
        return s


def score_case(case: GoldenCase, actual: dict) -> bool:
    if case.is_refusal:
        return all(not actual.get(field_name) for field_name in case.expected)

    for field_name, expected_value in case.expected.items():
        if _normalize(actual.get(field_name)) != _normalize(expected_value):
            return False
    return True