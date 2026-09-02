import csv
import time

import httpx

from config import settings
from prompts import PROMPTS


def call_ollama(prompt: str) -> tuple[dict, float]:
    body = {
        "model": settings.ollama_model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }

    last_exc = None
    for attempt in range(1, settings.max_retries + 1):
        start = time.perf_counter()
        try:
            with httpx.Client(timeout=settings.request_timeout_s) as client:
                response = client.post(f"{settings.ollama_base_url}/api/chat", json=body)
                response.raise_for_status()
                data = response.json()
            elapsed = time.perf_counter() - start
            return data, elapsed
        except httpx.RequestError as exc:
            last_exc = exc
            print(f"    attempt {attempt}/{settings.max_retries} failed: {type(exc).__name__} — retrying..."
                  if attempt < settings.max_retries else
                  f"    attempt {attempt}/{settings.max_retries} failed: {type(exc).__name__} — giving up.")
            if attempt < settings.max_retries:
                time.sleep(2 ** (attempt - 1))  # exponential backoff: 1s, 2s, 4s...

    raise last_exc


def run_local_bakeoff():
    rows = []

    for item in PROMPTS:
        print(f"\n{settings.ollama_model} (local) | {item['label']}...")
        try:
            data, elapsed = call_ollama(item["prompt"])
            answer = data["message"]["content"]

            eval_duration_sec = data.get("eval_duration", 0) / 1e9

            print(f"  wall_clock={elapsed:.2f}s  ollama_eval_time={eval_duration_sec:.2f}s")
            print(f"  answer: {answer[:150]}...")

            rows.append({
                "model": f"{settings.ollama_model} (local)",
                "prompt_id": item["id"],
                "prompt_label": item["label"],
                "latency_sec": round(elapsed, 3),
                "cost_usd": 0.0,  # no per-call cost running locally
                "total_tokens": data.get("eval_count", None),
                "answer": answer.replace("\n", " \\n "),
                "usable": "",
            })

        except httpx.RequestError as exc:
            print(f"  FAILED after {settings.max_retries} attempts: {type(exc).__name__} — is `ollama serve` running?")
            rows.append({
                "model": f"{settings.ollama_model} (local)",
                "prompt_id": item["id"],
                "prompt_label": item["label"],
                "latency_sec": None,
                "cost_usd": 0.0,
                "total_tokens": None,
                "answer": f"CALL FAILED after {settings.max_retries} attempts: {type(exc).__name__}: {exc}",
                "usable": "N",
            })

    with open("results_ollama.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n\nSaved {len(rows)} rows to results_ollama.csv")
    print("Next: fill in 'usable' as Y or N for each row, same as the OpenRouter results.")


if __name__ == "__main__":
    run_local_bakeoff()