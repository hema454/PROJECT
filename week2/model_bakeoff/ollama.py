
import csv
import time

import httpx

from prompts import PROMPTS

URL = "http://localhost:11434/api/chat"
MODEL = "llama3.1:8b"  # change to whatever you pulled with `ollama pull`


def call_ollama(prompt: str) -> tuple[dict, float]:
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    start = time.perf_counter()
    with httpx.Client(timeout=120.0) as client:  
        response = client.post(URL, json=body)
        response.raise_for_status()
        data = response.json()
    elapsed = time.perf_counter() - start
    return data, elapsed


def run_local_bakeoff():
    rows = []

    for item in PROMPTS:
        print(f"\n{MODEL} (local) | {item['label']}...")
        try:
            data, elapsed = call_ollama(item["prompt"])
            answer = data["message"]["content"]
            
            eval_duration_sec = data.get("eval_duration", 0) / 1e9

            print(f"  wall_clock={elapsed:.2f}s  ollama_eval_time={eval_duration_sec:.2f}s")
            print(f"  answer: {answer[:150]}...")

            rows.append({
                "model": f"{MODEL} (local)",
                "prompt_id": item["id"],
                "prompt_label": item["label"],
                "latency_sec": round(elapsed, 3),
                "cost_usd": 0.0,  # no per-call cost running locally
                "total_tokens": data.get("eval_count", None),
                "answer": answer.replace("\n", " \\n "),
                "usable": "",
            })

        except httpx.RequestError as exc:
            print(f"  FAILED: {type(exc).__name__} — is `ollama serve` running?")
            rows.append({
                "model": f"{MODEL} (local)",
                "prompt_id": item["id"],
                "prompt_label": item["label"],
                "latency_sec": None,
                "cost_usd": 0.0,
                "total_tokens": None,
                "answer": f"CALL FAILED: {type(exc).__name__}: {exc}",
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