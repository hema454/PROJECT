"""
Minimal tool-calling agent loop. No framework (no LangChain, no SDK abstraction
layer) — raw httpx calls to the Anthropic Messages API, same pattern as the
raw-httpx-to-OpenRouter approach from Week 1.

Run:
    export ANTHROPIC_API_KEY=sk-...
    python agent_loop.py            # live run against the real API
    python agent_loop.py --demo     # deterministic offline demo (no API key needed)
                                     # proves normal termination AND cap-hit termination
"""

import os
import sys
import json
import statistics
import httpx


# =============================================================================
# PART 1 — TWO TOOLS. Plain functions. Nothing about them knows an LLM exists.
# =============================================================================

def fetch_repo_info(owner: str, repo: str) -> dict:
    """TOOL 1 — fetches something. Live network call, no model involved."""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    resp = httpx.get(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "agent-loop-demo"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    return {
        "full_name": data["full_name"],
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "open_issues": data["open_issues_count"],
        "language": data["language"],
    }


def calculate_stats(numbers: list) -> dict:
    """TOOL 2 — calculates something. Pure computation, no network, no model."""
    if not numbers:
        raise ValueError("numbers cannot be empty")
    return {
        "count": len(numbers),
        "mean": statistics.mean(numbers),
        "median": statistics.median(numbers),
        "stdev": statistics.stdev(numbers) if len(numbers) > 1 else 0.0,
        "min": min(numbers),
        "max": max(numbers),
    }


TOOL_IMPL = {
    "fetch_repo_info": fetch_repo_info,
    "calculate_stats": calculate_stats,
}


# =============================================================================
# PART 2 — SCHEMAS (Anthropic tool-use format)
# =============================================================================

TOOLS = [
    {
        "name": "fetch_repo_info",
        "description": "Fetch live star/fork/open-issue counts for a public GitHub repo.",
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "GitHub org or user, e.g. 'anthropics'"},
                "repo": {"type": "string", "description": "Repo name, e.g. 'anthropic-sdk-python'"},
            },
            "required": ["owner", "repo"],
        },
    },
    {
        "name": "calculate_stats",
        "description": "Compute mean/median/stdev/min/max for a list of numbers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "numbers": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "The numbers to summarize.",
                }
            },
            "required": ["numbers"],
        },
    },
]


# =============================================================================
# PART 3 — CAP DECLARED BEFORE THE LOOP EXISTS.
# The loop function below cannot be written without this already being defined.
# =============================================================================

MAX_ITERATIONS = 4  # hard ceiling on model turns per run — non-negotiable


def call_model_live(messages):
    """Real call to the Anthropic Messages API. Raw httpx, no SDK."""
    api_key = os.environ["ANTHROPIC_API_KEY"]
    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 1024,
            "tools": TOOLS,
            "messages": messages,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def run_agent(user_prompt, call_model, verbose=True):
    """
    The loop. Send messages -> if model wants a tool, run it and feed the
    result back -> repeat. Stops on a non-tool_use response, OR at
    MAX_ITERATIONS, whichever comes first. Always terminates.
    """
    messages = [{"role": "user", "content": user_prompt}]

    for iteration in range(1, MAX_ITERATIONS + 1):
        response = call_model(messages)
        stop_reason = response["stop_reason"]
        content = response["content"]
        messages.append({"role": "assistant", "content": content})

        if verbose:
            kinds = [b["type"] for b in content]
            print(f"  [iter {iteration}] stop_reason={stop_reason} blocks={kinds}")

        if stop_reason != "tool_use":
            final_text = "".join(b["text"] for b in content if b["type"] == "text")
            return {"status": "done", "iterations": iteration, "final_text": final_text}

        # Execute every requested tool call, feed results back as a user turn.
        tool_results = []
        for block in content:
            if block["type"] == "tool_use":
                fn = TOOL_IMPL.get(block["name"])
                try:
                    result = fn(**block["input"])
                except Exception as e:
                    result = {"error": str(e)}
                if verbose:
                    print(f"           -> ran {block['name']}({block['input']}) = {result}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block["id"],
                    "content": json.dumps(result),
                })
        messages.append({"role": "user", "content": tool_results})

    # Cap hit — loop still terminates, just without a final answer.
    return {"status": "capped", "iterations": MAX_ITERATIONS, "final_text": None}


# =============================================================================
# DEMO — deterministic stand-ins for the model, so the cap-hit path is
# provable without depending on a live API key or a cooperative model.
# =============================================================================

def _text_block(t):
    return {"type": "text", "text": t}


def _tool_block(name, inp, tool_id):
    return {"type": "tool_use", "id": tool_id, "name": name, "input": inp}


def stub_model_normal(messages):
    """Scripted model: one tool call, then a final answer. Should NOT hit the cap."""
    n_prior_assistant_turns = sum(1 for m in messages if m["role"] == "assistant")
    if n_prior_assistant_turns == 0:
        return {
            "stop_reason": "tool_use",
            "content": [_tool_block("calculate_stats", {"numbers": [4, 8, 15, 16, 23, 42]}, "t1")],
        }
    return {
        "stop_reason": "end_turn",
        "content": [_text_block("The mean of that set is 18.0, computed by the tool.")],
    }


def stub_model_never_stops(messages):
    """Scripted model: always asks for another tool call, never returns text.
    Simulates a runaway/ambiguous-prompt failure mode. This is what the cap exists for."""
    n_prior_assistant_turns = sum(1 for m in messages if m["role"] == "assistant")
    return {
        "stop_reason": "tool_use",
        "content": [_tool_block("fetch_repo_info", {"owner": "anthropics", "repo": "anthropic-sdk-python"}, f"t{n_prior_assistant_turns}")],
    }


def run_demo():
    print(f"MAX_ITERATIONS = {MAX_ITERATIONS}\n")

    print("Demo A — normal termination (model stops on its own):")
    result_a = run_agent("Summarize these numbers: 4, 8, 15, 16, 23, 42", stub_model_normal)
    print(f"  -> {result_a}\n")
    assert result_a["status"] == "done"
    assert result_a["iterations"] < MAX_ITERATIONS

    print("Demo B — cap hit (model never stops calling tools):")
    result_b = run_agent("Look up a repo forever", stub_model_never_stops)
    print(f"  -> {result_b}\n")
    assert result_b["status"] == "capped"
    assert result_b["iterations"] == MAX_ITERATIONS
    assert result_b["final_text"] is None

    print("Both paths terminated. Cap demonstrably triggered in Demo B.")


if __name__ == "__main__":
    if "--demo" in sys.argv or "ANTHROPIC_API_KEY" not in os.environ:
        run_demo()
    else:
        result = run_agent(
            "What are the stats for 4, 8, 15, 16, 23, 42, and separately, "
            "how many stars does anthropics/anthropic-sdk-python have?",
            call_model_live,
        )
        print(result)