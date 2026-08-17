import time
import json
import logging
import os

import httpx
import tiktoken

from config import settings


# =========================================================
# Configuration
# =========================================================

USD_TO_INR = settings.usd_to_inr


# =========================================================
# Structured Logger
# =========================================================

logger = logging.getLogger("openrouter_cost")
logger.setLevel(logging.INFO)

if not logger.handlers:

    # Create logs directory automatically
    os.makedirs("logs", exist_ok=True)

    # Write structured JSON lines to a file
    file_handler = logging.FileHandler(
        "logs/openrouter.log",
        encoding="utf-8"
    )

    # Each log entry is already JSON,
    # so we only output the message itself.
    file_handler.setFormatter(
        logging.Formatter("%(message)s")
    )

    logger.addHandler(file_handler)

logger.propagate = False


# =========================================================
# Local Token Estimate
# =========================================================

def count_tokens_estimate(
    text: str,
    encoding_name: str = "cl100k_base"
) -> int:

    try:
        enc = tiktoken.get_encoding(encoding_name)

    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")

    return len(enc.encode(text))


# =========================================================
# Call OpenRouter
# =========================================================

def call_openrouter(
    model: str,
    messages: list,
    **kwargs
) -> dict:

    if not settings.openrouter_api_key:
        raise RuntimeError(
            "Set OPENROUTER_API_KEY in your environment first."
        )

    url = f"{settings.openrouter_base_url}/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "usage": {
            "include": True
        },
        **kwargs,
    }

    start = time.perf_counter()

    with httpx.Client(timeout=60.0) as client:

        response = client.post(
            url,
            headers=headers,
            json=payload
        )

    latency_ms = (
        time.perf_counter() - start
    ) * 1000

    response.raise_for_status()

    body = response.json()

    # Add our own latency information
    body["_latency_ms"] = latency_ms

    return body


# =========================================================
# Fetch OpenRouter Generation Statistics
# =========================================================

def fetch_generation_stats(
    gen_id,
    retries=8,
    delay=1.5,
    backoff=1.5
):

    url = f"{settings.openrouter_base_url}/generation"

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }

    wait = delay

    for attempt in range(1, retries + 1):

        response = httpx.get(
            url,
            headers=headers,
            params={"id": gen_id},
            timeout=10
        )

        # Generation statistics may not be
        # indexed immediately.
        if response.status_code == 404:

            if attempt < retries:

                print(
                    f"[generation stats] "
                    f"attempt {attempt}/{retries}: "
                    f"not indexed yet, "
                    f"waiting {wait:.1f}s..."
                )

                time.sleep(wait)

                wait *= backoff

                continue

        response.raise_for_status()

        return response.json()

    raise RuntimeError(
        "Generation statistics were not available "
        "after all retries."
    )


# =========================================================
# Main Run Function
# =========================================================

def run(
    model: str,
    prompt: str,
    **kwargs
) -> dict:

    # -----------------------------------------------------
    # Create chat message
    # -----------------------------------------------------

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]


    # -----------------------------------------------------
    # 1. Local token estimate
    # -----------------------------------------------------

    pre_call_estimate = count_tokens_estimate(prompt)

    print(
        "[pre-call estimate] "
        f"prompt tokens "
        f"(tiktoken, approximate): "
        f"{pre_call_estimate}"
    )


    # -----------------------------------------------------
    # 2. Call OpenRouter
    # -----------------------------------------------------

    result = call_openrouter(
        model,
        messages,
        **kwargs
    )


    # -----------------------------------------------------
    # 3. Get model response
    # -----------------------------------------------------

    try:

        answer = result[
            "choices"
        ][0][
            "message"
        ][
            "content"
        ]

        print("\n[model response]")
        print(answer)

    except (
        KeyError,
        IndexError,
        TypeError
    ):

        print(
            "\n[model response]"
        )

        print(
            "Unable to extract model response."
        )


    # -----------------------------------------------------
    # 4. Get provider usage
    # -----------------------------------------------------

    usage = result.get(
        "usage",
        {}
    )

    prompt_tokens = usage.get(
        "prompt_tokens"
    )

    completion_tokens = usage.get(
        "completion_tokens"
    )

    cost_usd = usage.get(
        "cost"
    )

    latency_ms = result[
        "_latency_ms"
    ]


    # -----------------------------------------------------
    # Make sure cost exists
    # -----------------------------------------------------

    if cost_usd is None:

        raise RuntimeError(
            "No 'cost' field in the response. "
            "OpenRouter did not return cost information."
        )


    # -----------------------------------------------------
    # 5. Convert USD to INR
    # -----------------------------------------------------

    cost_inr = (
        cost_usd
        * USD_TO_INR
    )


    # -----------------------------------------------------
    # 6. Print usage information
    # -----------------------------------------------------

    print("\n[response]")

    print(
        f"Prompt tokens:     "
        f"{prompt_tokens}"
    )

    print(
        f"Completion tokens: "
        f"{completion_tokens}"
    )

    print(
        f"Latency:           "
        f"{latency_ms:.2f} ms"
    )

    print(
        f"Cost:              "
        f"${cost_usd:.10f} "
        f"(₹{cost_inr:.6f})"
    )


    # -----------------------------------------------------
    # 7. Structured JSONL log
    # -----------------------------------------------------

    log_record = {

        "event":
            "openrouter_call",

        "model":
            model,

        "generation_id":
            result.get("id"),

        "prompt_tokens_estimate_local":
            pre_call_estimate,

        "prompt_tokens_provider":
            prompt_tokens,

        "completion_tokens_provider":
            completion_tokens,

        "latency_ms":
            round(
                latency_ms,
                3
            ),

        "cost_usd":
            cost_usd,

        "cost_inr":
            round(
                cost_inr,
                6
            ),

        "usd_to_inr_rate_used":
            USD_TO_INR,
    }


    # Write exactly one JSON object per line
    logger.info(
        json.dumps(
            log_record
        )
    )


    # =====================================================
    # 8. Reconcile with OpenRouter Generation Record
    # =====================================================

    gen_id = result.get(
        "id"
    )


    if not gen_id:

        print(
            "\n[verification]"
        )

        print(
            "❌ Cannot verify: "
            "generation ID was not returned."
        )

        return log_record


    try:

        stats = fetch_generation_stats(
            gen_id
        )

        stats_data = stats.get(
            "data",
            stats
        )


        # -------------------------------------------------
        # Get generation record values
        # -------------------------------------------------

        dashboard_cost = stats_data.get(
            "total_cost"
        )

        dashboard_prompt_tokens = (
            stats_data.get(
                "tokens_prompt"
            )
        )

        dashboard_completion_tokens = (
            stats_data.get(
                "tokens_completion"
            )
        )


        print(
            "\n[verification]"
        )


        # =================================================
        # COST VERIFICATION
        # =================================================

        if dashboard_cost is not None:

            cost_match = (
                abs(
                    float(cost_usd)
                    -
                    float(dashboard_cost)
                )
                < 1e-10
            )

            print(
                "\nCost:"
            )

            print(
                f"  API response = "
                f"${float(cost_usd):.10f}"
            )

            print(
                f"  Generation   = "
                f"${float(dashboard_cost):.10f}"
            )

            if cost_match:

                print(
                    "  Result       = "
                    "✅ MATCH"
                )

            else:

                print(
                    "  Result       = "
                    "❌ MISMATCH"
                )

        else:

            cost_match = False

            print(
                "\nCost:"
            )

            print(
                "  ⚠️ Generation "
                "record did not provide cost."
            )


        # =================================================
        # PROMPT TOKEN COMPARISON
        # =================================================

        if dashboard_prompt_tokens is not None:

            prompt_match = (
                int(prompt_tokens)
                ==
                int(dashboard_prompt_tokens)
            )

            print(
                "\nPrompt tokens:"
            )

            print(
                f"  API response = "
                f"{prompt_tokens}"
            )

            print(
                f"  Generation   = "
                f"{dashboard_prompt_tokens}"
            )

            if prompt_match:

                print(
                    "  Result       = "
                    "✅ MATCH"
                )

            else:

                print(
                    "  Result       = "
                    "⚠️ DIFFERENT"
                )


        # =================================================
        # COMPLETION TOKEN COMPARISON
        # =================================================

        if dashboard_completion_tokens is not None:

            completion_match = (
                int(completion_tokens)
                ==
                int(dashboard_completion_tokens)
            )

            print(
                "\nCompletion tokens:"
            )

            print(
                f"  API response = "
                f"{completion_tokens}"
            )

            print(
                f"  Generation   = "
                f"{dashboard_completion_tokens}"
            )

            if completion_match:

                print(
                    "  Result       = "
                    "✅ MATCH"
                )

            else:

                print(
                    "  Result       = "
                    "⚠️ DIFFERENT"
                )


        # =================================================
        # FINAL COST VERIFICATION
        # =================================================

        print(
            "\nFinal cost verification:"
        )

        if cost_match:

            print(
                "✅ MATCH — "
                "OpenRouter cost is verified."
            )

        else:

            print(
                "❌ MISMATCH — "
                "OpenRouter cost differs."
            )


        # =================================================
        # Log token differences separately
        # =================================================

        if (
            dashboard_prompt_tokens is not None
            and dashboard_completion_tokens is not None
        ):

            if (
                not prompt_match
                or not completion_match
            ):

                logger.info(
                    json.dumps(
                        {
                            "event":
                                "openrouter_token_difference",

                            "generation_id":
                                gen_id,

                            "api_prompt_tokens":
                                prompt_tokens,

                            "generation_prompt_tokens":
                                dashboard_prompt_tokens,

                            "api_completion_tokens":
                                completion_tokens,

                            "generation_completion_tokens":
                                dashboard_completion_tokens,
                        }
                    )
                )


    except httpx.HTTPStatusError as e:

        print(
            "\n[verification]"
        )

        print(
            "⚠️ Could not verify "
            f"generation record: {e}"
        )


    return log_record


# =========================================================
# Run Program
# =========================================================

if __name__ == "__main__":

    run(

        model="google/gemini-2.5-flash-lite",

        prompt=(
            "Explain the difference between "
            "BPE and WordPiece tokenization "
            "in two sentences."
        ),
    )