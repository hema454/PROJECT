"""
seed_prompts.py

One-time script to populate the prompts table with your real bake-off
prompts. Each prompt is fully self-contained — instruction AND content
together — so the model has something real to respond to (unlike the
earlier demo prompt, which was just an instruction with no article
attached).

Run once: uv run seed_prompts.py
Re-running is safe — it skips prompts that already exist by name.
"""

from store import add_prompt

BAKEOFF_PROMPTS = [
    {
        "name": "summarization_v1",
        "tags": "summarization",
        "text": """Summarize the article below in exactly 3 bullet points. Each bullet must state only a fact from the article.

<article>
The city council approved a $4.5M budget for downtown road repairs on Wednesday. The project will begin in April and is expected to take six months. Officials said the repairs will affect Main Street, Oak Avenue, and Third Street, with detours planned during peak construction. Local business owners expressed concern about reduced foot traffic during the repair period, while the mayor's office said the long-term infrastructure investment was necessary and overdue.
</article>""",
    },
    {
        "name": "classification_v1",
        "tags": "classification",
        "text": """Classify the sentiment of the review below as exactly one word: Positive, Negative, or Neutral.

<review>
The battery life is decent but the screen scratches way too easily. Customer support was helpful when I called about it though.
</review>""",
    },
    {
        "name": "extraction_v1",
        "tags": "extraction",
        "text": """Extract the following fields from the message below as JSON: name, email, company, urgent (boolean).

<message>
Hi, this is Priya Nair from Zentra Labs, [email protected]. We need this fixed URGENTLY before our demo tomorrow.
</message>""",
    },
    {
        "name": "reasoning_v1",
        "tags": "reasoning",
        "text": """A train leaves Station A at 60 km/h. Two hours later, a second train leaves the same station on the same track at 90 km/h. How long after the second train departs does it catch up to the first? Show your reasoning step by step, then give the final answer.""",
    },
    {
        "name": "creative_v1",
        "tags": "creative",
        "text": """Write a two-sentence product description for a reusable coffee cup made from recycled ocean plastic, aimed at environmentally-conscious young professionals.""",
    },
]


def main():
    for item in BAKEOFF_PROMPTS:
        try:
            add_prompt(name=item["name"], text=item["text"], tags=item["tags"])
            print(f"Added: {item['name']}")
        except Exception as e:
            print(f"Skipped {item['name']} (likely already exists): {e}")


if __name__ == "__main__":
    main()