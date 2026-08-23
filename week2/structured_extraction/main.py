"""
main.py

Runs structured extraction against a local Ollama model 50 times and
proves the pipeline survives malformed output:
  - On RecoveryError or ValidationError, retries ONCE with the error
    message fed back to the model.
  - If the retry also fails, the run is reported as a clean failure —
    never an unhandled crash.

Setup:
    1. Have Ollama running locally with a model pulled, e.g.:
         ollama pull llama3.2
    2. pip install httpx pydantic-settings json-repair --break-system-packages
    3. Run: uv run main.py   (or plain python main.py)

Output:
    Prints a per-run log and a final tally, and writes REPORT.md with
    every failed/recovered case for inspection.
"""

from pathlib import Path

import httpx
from pydantic import ValidationError

from config import settings
from extract import RecoveryError, parse_and_validate
from models import ExtractedContact

REPORT_PATH = Path(__file__).resolve().parent / "REPORT.md"

# A handful of unstructured inputs, cycled through across the 50 runs.
SAMPLE_TEXTS = [
    "Hi, this is Priya Nair from Zentra Labs, [email protected]. "
    "We need this fixed URGENTLY before our demo tomorrow.",

    "hey its rohan here (rohan.k@outbox.io), work at Brightline Co. "
    "no rush on this one whenever you get a chance",

    "Message from: Aditi Sharma | [email protected] | NovaWorks Inc | "
    "This is a critical, time-sensitive request — please treat as urgent.",

    "Hello, my name's Karthik, I'm reaching out from Solstice Systems. "
    "Email: [email protected]. Nothing urgent, just following up.",

    "URGENT — Meera Iyer (meera_iyer@quantail.com) from Quantail needs "
    "a response ASAP, this is blocking their release.",
]


def build_prompt(text: str) -> str:
    return f"""Extract contact info from the message below as a JSON object
with exactly these fields: name (string), email (string), company (string),
urgent (boolean, true only if the message explicitly signals urgency).

Return ONLY the JSON object.

Message:
{text}"""


def call_ollama(prompt: str) -> str:
    """Sends one prompt to a local Ollama model and returns the text response."""
    response = httpx.post(
        settings.ollama_base_url,
        json={
            "model": settings.ollama_model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        },
        timeout=60.0,
    )
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"]


def run_once(text: str, run_index: int) -> dict:
    """Runs one extraction attempt, with one retry on failure.
    Always returns a result dict — never raises."""
    prompt = build_prompt(text)

    try:
        raw = call_ollama(prompt)
    except httpx.HTTPError as e:
        return {"run": run_index, "status": "failed", "detail": f"Ollama request failed: {e}"}

    try:
        contact = parse_and_validate(raw, ExtractedContact)
        return {"run": run_index, "status": "success", "detail": contact.model_dump()}
    except (RecoveryError, ValidationError) as first_error:
        # Retry once, feeding the exact error back to the model.
        retry_prompt = f"""{prompt}

Your previous response could not be used because of this error:
{first_error}

Your previous response was:
{raw}

Please return ONLY a corrected JSON object matching the schema."""
        try:
            raw_retry = call_ollama(retry_prompt)
            contact = parse_and_validate(raw_retry, ExtractedContact)
            return {"run": run_index, "status": "recovered", "detail": contact.model_dump()}
        except httpx.HTTPError as e:
            return {"run": run_index, "status": "failed", "detail": f"Retry request failed: {e}"}
        except (RecoveryError, ValidationError) as second_error:
            return {
                "run": run_index,
                "status": "failed",
                "detail": f"Failed after retry — first: {first_error} | second: {second_error}",
            }


def main():
    print(f"Testing model: {settings.ollama_model} over {settings.num_runs} runs\n")

    results = []
    for i in range(settings.num_runs):
        text = SAMPLE_TEXTS[i % len(SAMPLE_TEXTS)]
        
        try:
            result = run_once(text, i + 1)
        except Exception as e:  # noqa: BLE001 — intentional catch-all per assignment spec
            result = {"run": i + 1, "status": "failed", "detail": f"Unexpected error: {e}"}
        results.append(result)
        print(f"Run {i + 1:>2}: {result['status']}")

    tally = {"success": 0, "recovered": 0, "failed": 0}
    for r in results:
        tally[r["status"]] += 1

    print("\n--- Summary ---")
    print(f"Success (first try): {tally['success']}")
    print(f"Recovered (after retry): {tally['recovered']}")
    print(f"Failed (reported cleanly): {tally['failed']}")
    print(f"Total runs: {len(results)} — zero crashes")

    write_report(results, tally)


def write_report(results: list[dict], tally: dict) -> None:
    lines = ["# Structured Extraction Report\n"]
    lines.append(f"**Model:** {settings.ollama_model}")
    lines.append(f"**Total runs:** {len(results)}")
    lines.append(f"**Success (first try):** {tally['success']}")
    lines.append(f"**Recovered (after retry):** {tally['recovered']}")
    lines.append(f"**Failed (reported cleanly):** {tally['failed']}\n")

    lines.append("## Non-success runs (recovered or failed)\n")
    for r in results:
        if r["status"] != "success":
            lines.append(f"- **Run {r['run']}** — {r['status']}: {r['detail']}")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nREPORT.md written to {REPORT_PATH}")


if __name__ == "__main__":
    main()