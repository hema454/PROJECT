import json
import asyncio
import httpx
from config import settings

PROMPT = "Name a color."  # short + simple so differences are easy to eyeball
MODEL = "openai/gpt-4o-mini"

HEADERS = {
    "Authorization": f"Bearer {settings.openrouter_api_key}",
    "Content-Type": "application/json",
}
URL = f"{settings.openrouter_base_url}/chat/completions"


async def call(client: httpx.AsyncClient, prompt, temperature, max_tokens=None):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens

    resp = await client.post(URL, headers=HEADERS, json=payload)

    if resp.status_code != 200:
        return {"error": True, "status": resp.status_code, "body": resp.json()}

    body = resp.json()
    choice = body["choices"][0]
    return {
        "error": False,
        "text": choice["message"]["content"],
        "finish_reason": choice.get("finish_reason"),
    }


async def run_repeats(client: httpx.AsyncClient, prompt, temperature, n=10):
    # All n calls fire at once instead of waiting on each other.
    results = await asyncio.gather(*(call(client, prompt, temperature) for _ in range(n)))
    for i, r in enumerate(results):
        print(f"  [{i+1}/{n}] temp={temperature}: {r.get('text', r).__repr__()[:80]}")
    return results


async def step_1_and_2(client: httpx.AsyncClient):
    print("\n=== Step 1+2: 10x at temp=0, 10x at temp=1.0 ===")
    # The two temperature batches also run concurrently with each other.
    temp0_results, temp1_results = await asyncio.gather(
        run_repeats(client, PROMPT, 0.0, n=10),
        run_repeats(client, PROMPT, 1.0, n=10),
    )

    temp0_unique = {r["text"] for r in temp0_results if not r["error"]}
    temp1_unique = {r["text"] for r in temp1_results if not r["error"]}

    print(f"\ntemp=0 unique outputs: {len(temp0_unique)} -> {temp0_unique}")
    print(f"temp=1.0 unique outputs: {len(temp1_unique)} -> {temp1_unique}")

    return temp0_results, temp1_results


async def step_3_low_max_tokens(client: httpx.AsyncClient):
    print("\n=== Step 3: max_tokens deliberately too low ===")
    long_prompt = "Write a detailed 300-word explanation of how photosynthesis works."
    r = await call(client, long_prompt, temperature=0.7, max_tokens=10)
    print(f"finish_reason: {r.get('finish_reason')}")
    print(f"text: {r.get('text')}")
    return r


async def step_4_context_overflow(client: httpx.AsyncClient):
    print("\n=== Step 4: prompt larger than context window ===")
    # gpt-4o-mini's context is ~128k tokens; repeating a word is a cheap way
    # to blow past that without needing real content.
    huge_prompt = "word " * 200_000  # ~200k tokens, comfortably over the limit
    r = await call(client, huge_prompt, temperature=0.0)
    print(json.dumps(r, indent=2)[:1500])
    return r


async def main():
    all_results = {}
    async with httpx.AsyncClient(timeout=60.0) as client:
        all_results["temp0"], all_results["temp1"] = await step_1_and_2(client)
        all_results["low_max_tokens"] = await step_3_low_max_tokens(client)
        all_results["context_overflow"] = await step_4_context_overflow(client)

    with open("temp_experiment_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    print("\nSaved full results to temp_experiment_results.json")


if __name__ == "__main__":
    asyncio.run(main())