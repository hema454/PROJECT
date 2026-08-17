"""
Batch mode — Concepts 1.20, 1.21

Usage:
    python batch_mode.py prompts.txt

prompts.txt: one prompt per line, blank lines ignored.
"""
import sys
import time
import asyncio
import httpx
from config import settings

MODEL = "openai/gpt-4o-mini"
URL = f"{settings.openrouter_base_url}/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {settings.openrouter_api_key}",
    "Content-Type": "application/json",
}


def load_prompts(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


async def call_one(client: httpx.AsyncClient, prompt: str) -> dict:
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "usage": {"include": True},
    }
    start = time.perf_counter()
    resp = await client.post(URL, headers=HEADERS, json=payload)
    latency_ms = (time.perf_counter() - start) * 1000

    if resp.status_code != 200:
        return {"error": True, "prompt": prompt, "status": resp.status_code,
                "body": resp.json(), "latency_ms": latency_ms}

    body = resp.json()
    usage = body.get("usage", {})
    return {
        "error": False,
        "prompt": prompt,
        "text": body["choices"][0]["message"]["content"],
        "cost_usd": usage.get("cost", 0.0),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "latency_ms": latency_ms,
    }


async def run_concurrent(prompts: list[str]) -> tuple[list[dict], float]:
    async with httpx.AsyncClient(timeout=60.0) as client:
        start = time.perf_counter()
        results = await asyncio.gather(*(call_one(client, p) for p in prompts))
        elapsed = time.perf_counter() - start
    return results, elapsed


async def run_sequential(prompts: list[str]) -> tuple[list[dict], float]:
    async with httpx.AsyncClient(timeout=60.0) as client:
        start = time.perf_counter()
        results = []
        for p in prompts:
            results.append(await call_one(client, p))
        elapsed = time.perf_counter() - start
    return results, elapsed


def summarize(label: str, results: list[dict], elapsed: float):
    ok = [r for r in results if not r["error"]]
    failed = [r for r in results if r["error"]]
    total_cost = sum(r["cost_usd"] for r in ok)
    avg_cost = total_cost / len(ok) if ok else 0.0
    slowest = max((r["latency_ms"] for r in results), default=0.0)

    print(f"\n=== {label} ===")
    print(f"  prompts: {len(results)}  ok: {len(ok)}  failed: {len(failed)}")
    print(f"  total elapsed: {elapsed*1000:.1f} ms")
    print(f"  slowest single call: {slowest:.1f} ms")
    print(f"  total cost: ${total_cost:.8f}")
    print(f"  avg cost/prompt: ${avg_cost:.8f}")
    if failed:
        print(f"  failures: {[f['status'] for f in failed]}")
    return total_cost


async def main(path: str):
    prompts = load_prompts(path)
    print(f"Loaded {len(prompts)} prompts from {path}")

    concurrent_results, concurrent_elapsed = await run_concurrent(prompts)
    concurrent_cost = summarize("CONCURRENT (asyncio.gather)", concurrent_results, concurrent_elapsed)

    sequential_results, sequential_elapsed = await run_sequential(prompts)
    sequential_cost = summarize("SEQUENTIAL (one after another)", sequential_results, sequential_elapsed)

    print("\n=== Comparison ===")
    print(f"  concurrent: {concurrent_elapsed:.2f}s")
    print(f"  sequential: {sequential_elapsed:.2f}s")
    print(f"  speedup: {sequential_elapsed / concurrent_elapsed:.1f}x")
    print(f"  cost is ~same either way: concurrent=${concurrent_cost:.8f}  "
          f"sequential=${sequential_cost:.8f}  (concurrency changes latency, not cost)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python batch_mode.py prompts.txt")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))