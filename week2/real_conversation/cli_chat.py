

import argparse
import sys

from openai import OpenAI

from config import settings

OPENROUTER_BASE_URL = settings.openrouter_base_url

_warned_unpriced_models = set()


def cost_for(pricing: dict, model: str, input_tokens: int, output_tokens: int) -> float:
    """USD cost of one response, given the model's usage counts."""
    rates = pricing.get(model)
    if rates is None:
        if model not in _warned_unpriced_models:
            _warned_unpriced_models.add(model)
            print(
                f"[warning] no pricing entry for {model!r} — its cost will show as $0.00. "
                f"Add it under \"pricing\" in config.py to track it accurately.",
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
    parser.add_argument("--primary", default=None, help="Primary model id, e.g. openai/gpt-5-mini (overrides .env)")
    parser.add_argument("--fallback", default=None, help="Fallback model id (overrides .env)")
    parser.add_argument("--system", default=None, help="System prompt (overrides .env)")
    parser.add_argument("--max-tokens", type=int, default=None, help="Max output tokens per turn (overrides .env)")
    parser.add_argument(
        "--break-after",
        type=int,
        default=None,
        metavar="N",
        help="Deliberately corrupt the primary model id after N successful turns, "
        "to prove the fallback path works. You can also type '!break' mid-chat.",
    )
    args = parser.parse_args()

    primary_model = args.primary or settings.primary_model
    fallback_model = args.fallback or settings.fallback_model
    system_prompt = args.system or settings.system_prompt
    max_tokens = args.max_tokens or settings.max_tokens
    pricing = settings.pricing

    # OpenRouter speaks the OpenAI Chat Completions API — same SDK, just a
    # different base_url and key.
    client = OpenAI(base_url=settings.openrouter_base_url, api_key=settings.openrouter_api_key)

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