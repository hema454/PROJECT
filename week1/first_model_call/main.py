import json
import httpx

from config import settings


URL = f"{settings.openrouter_base_url}/chat/completions"


def call_model(prompt: str) -> dict:
    """Send a raw HTTP POST request to OpenRouter."""

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }

    body = {
        "model": settings.model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Answer the user's question directly and confidently. "
                    "Do not add unnecessary disclaimers."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": settings.temperature,
    }

    response = httpx.post(
        URL,
        headers=headers,
        json=body,
        timeout=60.0,
    )

    response.raise_for_status()

    return response.json()


def print_result(label: str, prompt: str) -> None:
    """Print the generated answer and the complete raw JSON response."""

    print("=" * 80)
    print(f"TEST: {label}")
    print("=" * 80)

    print("\nPROMPT:")
    print(prompt)

    data = call_model(prompt)

    answer = data["choices"][0]["message"]["content"]

    print("\nMODEL ANSWER:")
    print(answer)

    print("\nRAW JSON RESPONSE:")
    print(json.dumps(data, indent=2))

    print("\n")


if __name__ == "__main__":

    # ---------------------------------------------------------------
    # 1. Normal model call
    # ---------------------------------------------------------------

    print_result(
        "NORMAL CALL",
        "What is the capital of France?"
    )

    # ---------------------------------------------------------------
    # 2. Hallucination attempt #1:
    #    Ask about information after the model's knowledge cutoff.
    # ---------------------------------------------------------------

    # 1. After knowledge cutoff
# 1. Knowledge cutoff
print_result(
    "post-cutoff",
    "In September 2025, the Nobel Prize in Physics was awarded to "
    "three scientists. Complete this sentence with their names and "
    "the official Nobel citation: 'The 2025 Nobel Prize in Physics "
    "was awarded to ...'"
)

# 2. Nonexistent person
print_result(
    "nonexistent person",
    "Complete this biographical paragraph: "
    "'Dr. Elowen Marchetti-Vance was born in 1968 and became famous "
    "for inventing the Marchetti-Vance compression algorithm in 1994. "
    "She studied at ...'"
)

# 3. Citation
print_result(
    "citation",
    "Complete the following academic reference in APA format: "
    "Tanaka, Y. (1987). Attention-based neural computation. "
    "Journal of Artificial Intelligence, ..."
)