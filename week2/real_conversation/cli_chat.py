#!/usr/bin/env python3
"""
chat_cli.py — a small multi-turn OpenRouter chat CLI with streaming,
automatic provider fallback, and running cost tracking.

Requirements:
    pip install openai python-dotenv

Auth:
    Create a .env file next to this script containing:
        OPENROUTER_API_KEY=sk-or-v1-...
    (add .env to .gitignore — never commit real keys)
    Get a key at https://openrouter.ai/keys

Config:
    Settings (which models to use, system prompt, max tokens, pricing table)
    live in config.json next to this script — see config.example.json for the
    shape. Any CLI flag you pass overrides the matching config value.
    Model ids must be OpenRouter slugs — vendor/model, e.g. "openai/gpt-5-mini"
    or "meta-llama/llama-3.3-70b-instruct". Look them up at openrouter.ai/models.

Run:
    python chat_cli.py
    python chat_cli.py --config myconfig.json
    python chat_cli.py --primary anthropic/claude-sonnet-5   # overrides config.json for this run
    python chat_cli.py --break-after 2      # auto-break the primary model after 2 turns
    # or, inside the chat, type:  !break     # break the primary model right now

Type 'exit' or 'quit' to leave the conversation.

--------------------------------------------------------------------------
WHAT THIS DEMONSTRATES
--------------------------------------------------------------------------
1. Multi-turn history: every request resends the full `messages` list, since
   the OpenAI-compatible Chat Completions API is stateless — the server has
   no memory of prior calls.
2. Streaming: tokens print as they arrive via `client.chat.completions.create(
   stream=True)`.
3. Fallback: each turn is tried on PRIMARY_MODEL first. If that call raises
   (auth error, rate limit, invalid model, connection error, etc.) *before
   any output has been printed*, we transparently retry on FALLBACK_MODEL —
   the user sees one coherent answer, never a half-written broken one.
   `--break-after N` (or the in-chat `!break` command) corrupts the primary
   model id after N turns so you can watch a real API error get caught and
   silently routed around.
4. Cost: usage.prompt_tokens / usage.completion_tokens come back via
   stream_options={"include_usage": True}. We price them per OpenRouter's
   published rates and print a running total after each turn — watch it
   climb as the resent history grows.

Pricing source (verified 2026-08-19): https://openrouter.ai/models
Prices change over time and vary by provider routing — re-check before
trusting this for real billing.
--------------------------------------------------------------------------
"""

import argparse
import json
import os
import sys

from openai import OpenAI
from dotenv import dotenv_values

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# ---------------------------------------------------------------------------
# Built-in fallback defaults, used only for keys the config file doesn't set
# (or if no config file exists at all). USD per million tokens.
# Verified 2026-08-19: https://openrouter.ai/models
# ---------------------------------------------------------------------------
BUILTIN_PRICING_PER_MTOK = {
    "openai/gpt-5-mini": {"input": 0.25, "output": 2.00},
    "meta-llama/llama-3.3-70b-instruct": {"input": 0.10, "output": 0.32},
}
BUILTIN_DEFAULTS = {
    "primary_model": "openai/gpt-5-mini",  # primary model to try first
    "fallback_model": "meta-llama/llama-3.3-70b-instruct",  # fallback if primary fails
    "system_prompt": "You are a helpful, concise assistant.",
    "max_tokens": 1024,
}


def load_config(path: str) -> dict:
    """
    Load settings from a JSON config file. Missing file is fine (you just
    get BUILTIN_DEFAULTS / BUILTIN_PRICING_PER_MTOK). Malformed JSON is not
    fine — fail loudly rather than silently ignoring a typo'd config.

    Config keys (all optional): primary_model, fallback_model, system_prompt,
    max_tokens, pricing (a dict of model_id -> {"input": x, "output": y}).
    """
    config = dict(BUILTIN_DEFAULTS)
    config["pricing"] = dict(BUILTIN_PRICING_PER_MTOK)

    if not os.path.exists(path):
        return config

    with open(path, "r", encoding="utf-8") as f:
        try:
            user_config = json.load(f)
        except json.JSONDecodeError as exc:
            print(f"[error] {path} is not valid JSON: {exc}", file=sys.stderr)
            sys.exit(1)

    for key in ("primary_model", "fallback_model", "system_prompt", "max_tokens"):
        if key in user_config:
            config[key] = user_config[key]

    # Pricing entries from the config file are merged in on top of the
    # built-ins (a config entry overrides a built-in with the same model id;
    # built-ins for models the config doesn't mention are kept).
    config["pricing"].update(user_config.get("pricing", {}))

    return config


_warned_unpriced_models = set()


def cost_for(pricing: dict, model: str, input_tokens: int, output_tokens: int) -> float:
    """USD cost of one response, given the model's usage counts."""
    rates = pricing.get(model)
    if rates is None:
        if model not in _warned_unpriced_models:
            _warned_unpriced_models.add(model)
            print(
                f"[warning] no pricing entry for {model!r} — its cost will show as $0.00. "
                f"Add it under \"pricing\" in your config file to track it accurately.",
                file=sys.stderr,
            )
        return 0.0
    return (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000


class TurnResult:
    """Everything about one completed model turn."""

    def __init__(self, text, model_used, input_tokens, output_tokens, used_fallback, pricing):
        self.text = text
        self.model_used = model_used
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.used_fallback = used_fallback
        self.cost = cost_for(pricing, model_used, input_tokens, output_tokens)


def stream_once(client: OpenAI, model: str, history: list, system: str, max_tokens: int, pricing: dict) -> TurnResult:
    """
    Make ONE streaming call to `model` via OpenRouter's OpenAI-compatible
    Chat Completions endpoint. Prints tokens to stdout as they arrive.
    Raises whatever the SDK raises (APIStatusError, APIConnectionError,
    etc.) on failure — the caller decides what to do about it.

    Unlike Anthropic's Messages API, Chat Completions puts the system
    prompt IN the messages list (role="system") rather than as a separate
    parameter, so we prepend it here.
    """
    full_messages = [{"role": "system", "content": system}] + history

    full_text_parts = []
    prompt_tokens = 0
    completion_tokens = 0

    stream = client.chat.completions.create(
        model=model,
        messages=full_messages,
        max_tokens=max_tokens,
        stream=True,
        # Without this, the streamed chunks never carry token counts —
        # OpenRouter (like OpenAI) only attaches `usage` to a final chunk
        # when you explicitly ask for it.
        stream_options={"include_usage": True},
    )

    for chunk in stream:
        if chunk.choices:
            delta = chunk.choices[0].delta.content
            if delta:
                print(delta, end="", flush=True)
                full_text_parts.append(delta)
        if chunk.usage:
            prompt_tokens = chunk.usage.prompt_tokens
            completion_tokens = chunk.usage.completion_tokens

    print()  # newline after the streamed answer
    return TurnResult(
        text="".join(full_text_parts),
        model_used=model,
        input_tokens=prompt_tokens,
        output_tokens=completion_tokens,
        used_fallback=False,
        pricing=pricing,
    )


class BothProvidersFailedError(Exception):
    """Raised when both the primary and fallback model calls fail."""


def get_completion(client, history, system, primary_model, fallback_model, max_tokens, pricing) -> TurnResult:
    
    try:
        return stream_once(client, primary_model, history, system, max_tokens, pricing)
    except Exception as primary_exc:
        # Quiet, developer-facing note on stderr only — the user's terminal
        # (stdout) never sees an error; they just get their answer a beat
        # later, from the fallback model.
        print(
            f"\n[fallback] {primary_model} failed ({type(primary_exc).__name__}: {primary_exc}); "
            f"retrying on {fallback_model}",
            file=sys.stderr,
        )
        try:
            result = stream_once(client, fallback_model, history, system, max_tokens, pricing)
        except Exception as fallback_exc:
            raise BothProvidersFailedError(
                f"primary ({primary_model}) failed: {type(primary_exc).__name__}: {primary_exc} | "
                f"fallback ({fallback_model}) also failed: {type(fallback_exc).__name__}: {fallback_exc}"
            ) from fallback_exc
        result.used_fallback = True
        return result


def main():
    parser = argparse.ArgumentParser(description="Multi-turn OpenRouter chat CLI with fallback and cost tracking.")
    parser.add_argument("--config", default="config.json", help="Path to JSON config file (default: config.json)")
    parser.add_argument("--primary", default=None, help="Primary model id, e.g. openai/gpt-5-mini (overrides config)")
    parser.add_argument("--fallback", default=None, help="Fallback model id (overrides config)")
    parser.add_argument("--system", default=None, help="System prompt (overrides config)")
    parser.add_argument("--max-tokens", type=int, default=None, help="Max output tokens per turn (overrides config)")
    parser.add_argument(
        "--break-after",
        type=int,
        default=None,
        metavar="N",
        help="Deliberately corrupt the primary model id after N successful turns, "
        "to prove the fallback path works. You can also type '!break' mid-chat.",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    # CLI flags take precedence over config file values, which take
    # precedence over the built-in defaults baked into load_config().
    primary_model = args.primary or config["primary_model"]
    fallback_model = args.fallback or config["fallback_model"]
    system_prompt = args.system or config["system_prompt"]
    max_tokens = args.max_tokens or config["max_tokens"]
    pricing = config["pricing"]

    # Read .env into its own dict (dotenv_values), NOT into os.environ
    # (load_dotenv would do that). Keeps the API key scoped to this dict
    # instead of leaking into the whole process's environment.
    env_config = dotenv_values(".env")
    api_key = env_config.get("OPENROUTER_API_KEY")
    if not api_key:
        print(
            "OPENROUTER_API_KEY not found in .env. Create a .env file next to this script with:\n"
            "  OPENROUTER_API_KEY=sk-or-v1-...\n"
            "Get a key at https://openrouter.ai/keys\n",
            file=sys.stderr,
        )
        sys.exit(1)

    # OpenRouter speaks the OpenAI Chat Completions API — same SDK, just a
    # different base_url and key.
    client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)

    # Mutable holder so we can "break" the primary model id from inside the loop.
    state = {"primary_model": primary_model, "turns": 0}

    
    history = []

    running_cost = 0.0

    print(f"Chatting with {state['primary_model']} (fallback: {fallback_model}). Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            break

        if user_input == "!break":
            state["primary_model"] = primary_model + "-BROKEN-ON-PURPOSE"
            print(f"[debug] primary model id corrupted -> {state['primary_model']!r}\n", file=sys.stderr)
            continue

        history.append({"role": "user", "content": user_input})

        print("assistant> ", end="", flush=True)
        try:
            result = get_completion(
                client, history, system_prompt, state["primary_model"], fallback_model, max_tokens, pricing
            )
        except BothProvidersFailedError as exc:
            # Both models are down — nothing left to fall back to. Report it
            # cleanly, undo the user turn we optimistically appended (so a
            # retry doesn't duplicate it), and keep the REPL alive.
            print(f"\n[error] {exc}\n", file=sys.stderr)
            history.pop()
            continue
        history.append({"role": "assistant", "content": result.text})

        state["turns"] += 1
        running_cost += result.cost

        if args.break_after is not None and state["turns"] == args.break_after:
            state["primary_model"] = primary_model + "-BROKEN-ON-PURPOSE"
            print(
                f"[debug] auto-break triggered after {args.break_after} turns "
                f"-> primary is now {state['primary_model']!r}",
                file=sys.stderr,
            )

        tag = f" (served by fallback: {result.model_used})" if result.used_fallback else ""
        print(
            f"  [turn {state['turns']}] "
            f"{result.input_tokens} in / {result.output_tokens} out tokens, "
            f"${result.cost:.6f} this turn, ${running_cost:.6f} running total{tag}\n"
        )


if __name__ == "__main__":
    main()