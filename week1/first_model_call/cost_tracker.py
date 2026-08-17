import time
import json
import logging
import httpx
import tiktoken
from config import settings

class OpenRouterClient:
    def __init__(self):
        self.base_url = settings.openrouter_base_url
        self.api_key = settings.openrouter_api_key

USD_TO_INR = settings.usd_to_inr

# ---- structured logger: emits raw JSON lines, no timestamp/level prefix ----
logger = logging.getLogger("openrouter_cost")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)
logger.propagate = False


def count_tokens_estimate(text: str, encoding_name: str = "cl100k_base") -> int:

    try:
        enc = tiktoken.get_encoding(encoding_name)
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def call_openrouter(model: str, messages: list, **kwargs) -> dict:
    """Calls chat/completions with usage accounting turned on."""
    if not settings.openrouter_api_key:
        raise RuntimeError("Set OPENROUTER_API_KEY in your environment first.")

    url = f"{settings.openrouter_base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "usage": {"include": True},
        **kwargs,
    }

    start = time.perf_counter()
    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, headers=headers, json=payload)
    latency_ms = (time.perf_counter() - start) * 1000

    response.raise_for_status()
    body = response.json()
    body["_latency_ms"] = latency_ms
    return body


def fetch_generation_stats(gen_id, retries=8, delay=1.5, backoff=1.5):
    """Polls OpenRouter's /generation endpoint, retrying on 404 since
    stats aren't indexed immediately after the completion call returns.
    Uses exponential backoff: 1.5s, 2.25s, 3.4s, ... up to `retries` attempts."""
    url = f"https://openrouter.ai/api/v1/generation?id={gen_id}"
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }
    resp = None
    wait = delay
    for attempt in range(1, retries + 1):
        resp = httpx.get(url, headers=headers, timeout=10)
        if resp.status_code == 404:
            print(f"[generation stats] attempt {attempt}/{retries}: not indexed yet, "
                  f"waiting {wait:.1f}s...")
            time.sleep(wait)
            wait *= backoff
            continue
        resp.raise_for_status()
        return resp.json()
    resp.raise_for_status()  # raise the final 404 if all retries exhausted


def run(model: str, prompt: str, **kwargs) -> dict:
    messages = [{"role": "user", "content": prompt}]

    # 1. Count tokens before sending
    pre_call_estimate = count_tokens_estimate(prompt)
    print(f"[pre-call estimate] prompt tokens (tiktoken, approximate): {pre_call_estimate}")

    # 2. Make the call
    result = call_openrouter(model, messages, **kwargs)

    usage = result.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens")
    completion_tokens = usage.get("completion_tokens")
    latency_ms = result["_latency_ms"]
    cost_usd = usage.get("cost")

    if cost_usd is None:
        raise RuntimeError(
            "No 'cost' field in the response - either usage.include wasn't "
            "honored, or this model/key combination doesn't report cost."
        )

    cost_inr = cost_usd * USD_TO_INR

    # 3. Print the numbers
    print(f"[response] prompt tokens (provider-reported): {prompt_tokens}")
    print(f"[response] completion tokens: {completion_tokens}")
    print(f"[response] latency: {latency_ms:.2f} ms")
    print(f"[response] cost: ${cost_usd:.10f}  (₹{cost_inr:.6f})")

    # 4. Structured log line - json.dumps through logging, never a print
    log_record = {
        "event": "openrouter_call",
        "model": model,
        "generation_id": result.get("id"),
        "prompt_tokens_estimate_local": pre_call_estimate,
        "prompt_tokens_provider": prompt_tokens,
        "completion_tokens_provider": completion_tokens,
        "latency_ms": round(latency_ms, 3),
        "cost_usd": cost_usd,
        "cost_inr": round(cost_inr, 6),
        "usd_to_inr_rate_used": USD_TO_INR,
    }
    logger.info(json.dumps(log_record))

    # 5. Reconcile against OpenRouter's own generation record
    gen_id = result.get("id")
    if gen_id:
        try:
            stats = fetch_generation_stats(gen_id)
        except httpx.HTTPStatusError as e:
            print(f"[generation stats] gave up reconciling with dashboard: {e}")
            stats = None

    if gen_id and stats:
        stats_data = stats.get("data", stats)  # API wraps fields under "data"
        dashboard_cost = stats_data.get("total_cost")
        dashboard_prompt_tokens = stats_data.get("tokens_prompt")
        dashboard_completion_tokens = stats_data.get("tokens_completion")

        mismatch = {}
        if dashboard_cost is not None and round(dashboard_cost, 10) != round(cost_usd, 10):
            mismatch["cost_usd"] = {"reported": cost_usd, "dashboard": dashboard_cost}
        if dashboard_prompt_tokens is not None and dashboard_prompt_tokens != prompt_tokens:
            mismatch["prompt_tokens"] = {"reported": prompt_tokens, "dashboard": dashboard_prompt_tokens}
        if dashboard_completion_tokens is not None and dashboard_completion_tokens != completion_tokens:
            mismatch["completion_tokens"] = {"reported": completion_tokens, "dashboard": dashboard_completion_tokens}

        if mismatch:
            logger.info(json.dumps({
                "event": "openrouter_cost_mismatch",
                "generation_id": gen_id,
                "mismatch": mismatch,
            }))
            print(f"MISMATCH vs dashboard: {mismatch}")
        else:
            print(f"Verified: cost (${dashboard_cost:.10f}) matches OpenRouter's generation record exactly.")

    return log_record


if __name__ == "__main__":
    run(
        model="openai/gpt-4o-mini",
        prompt="Explain the difference between BPE and WordPiece tokenization in two sentences.",
    )