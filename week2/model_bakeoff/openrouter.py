import csv
import time

import httpx

from config import settings
from prompts import PROMPTS

URL = f"{settings.openrouter_base_url}/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {settings.openrouter_api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://example.com",
    "X-Title": "Task 2.1 - Model Bake-off",
}


MODELS = settings.openrouter_models


def prompt_fields(item) -> tuple[str, str, str]:

    if isinstance(item, dict):
        pid = item.get("id", "")
        category = item.get("label") or item.get("category", "")
        text = item.get("prompt") or item.get("text", "")
        return pid, category, text

    return item.id, item.category, item.text


def call_model(model: str, prompt: str) -> tuple[dict, float]:
    """Returns (response_json, latency_seconds). Retries on transient
    request errors (timeouts, connection issues) up to settings.max_retries
    times, with exponential backoff. Does NOT retry on HTTP error responses
    (4xx/5xx) — those are raised immediately since retrying a bad request
    or an auth failure won't fix it."""
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": settings.max_output_tokens,
        "usage": {"include": True},
    }

    last_exc = None
    for attempt in range(1, settings.max_retries + 1):
        start = time.perf_counter()
        try:
            with httpx.Client(timeout=settings.request_timeout_s) as client:
                response = client.post(URL, headers=HEADERS, json=body)
                response.raise_for_status()
                data = response.json()
            elapsed = time.perf_counter() - start
            return data, elapsed
        except httpx.RequestError as exc:
            last_exc = exc
            if attempt < settings.max_retries:
                print(f"    attempt {attempt}/{settings.max_retries} failed: {type(exc).__name__} — retrying...")
                time.sleep(2 ** (attempt - 1))  # 1s, 2s, 4s...
            else:
                print(f"    attempt {attempt}/{settings.max_retries} failed: {type(exc).__name__} — giving up.")

    raise last_exc


def run_bakeoff():
    rows = []

    for model in MODELS:
        for item in PROMPTS:
            pid, category, text = prompt_fields(item)
            print(f"\n{model} | {category} ({pid})...")
            try:
                data, elapsed = call_model(model, text)
                answer = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                cost = usage.get("cost")
                total_tokens = usage.get("total_tokens")
                prompt_tokens = usage.get("prompt_tokens")
                completion_tokens = usage.get("completion_tokens")

                if cost is None:
                    print(f"  [warn] usage.cost still missing — response usage block was: {usage}")

                print(f"  latency={elapsed:.2f}s  cost=${cost}  tokens={total_tokens}")
                print(f"  answer: {answer[:150]}...")

                rows.append({
                    "model": model,
                    "prompt_id": pid,
                    "prompt_category": category,
                    "latency_sec": round(elapsed, 3),
                    "cost_usd": cost,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "answer": answer.replace("\n", " \\n "),
                    "usable": "",  # <-- fill this in by hand after reading "answer"
                })

            except httpx.HTTPStatusError as exc:
                print(f"  FAILED: {exc.response.status_code}")
                rows.append({
                    "model": model,
                    "prompt_id": pid,
                    "prompt_category": category,
                    "latency_sec": None,
                    "cost_usd": None,
                    "prompt_tokens": None,
                    "completion_tokens": None,
                    "total_tokens": None,
                    "answer": f"CALL FAILED: {exc.response.status_code} {exc.response.text[:200]}",
                    "usable": "N",  # a failed call is definitionally not usable
                })
            except httpx.RequestError as exc:
                print(f"  FAILED after {settings.max_retries} attempts: {type(exc).__name__}")
                rows.append({
                    "model": model,
                    "prompt_id": pid,
                    "prompt_category": category,
                    "latency_sec": None,
                    "cost_usd": None,
                    "prompt_tokens": None,
                    "completion_tokens": None,
                    "total_tokens": None,
                    "answer": f"CALL FAILED after {settings.max_retries} attempts: {type(exc).__name__}: {exc}",
                    "usable": "N",
                })

    with open("results_openrouter.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n\nSaved {len(rows)} rows to results_openrouter.csv")
    print("Next: open that file, read each 'answer', and fill in 'usable' as Y or N.")


if __name__ == "__main__":
    run_bakeoff()