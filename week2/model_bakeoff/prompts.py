"""
Five prompts representing the actual work an assistant would do day to day.
Kept identical across every model so the comparison is fair — same input,
different model, measure what changes.
"""

PROMPTS = [
    {
        "id": "summarize",
        "label": "Summarize a paragraph",
        "prompt": (
            "Summarize the following in 2 sentences, plain language, no jargon:\n\n"
            "Retrieval-augmented generation (RAG) is a technique that combines "
            "a language model with an external retrieval step. Instead of relying "
            "solely on knowledge baked into the model's parameters during training, "
            "the system first searches a knowledge base or document store for "
            "relevant passages, then inserts those passages into the prompt before "
            "generation. This grounds the model's output in retrieved, verifiable "
            "text rather than the model's internal (and potentially outdated or "
            "hallucinated) recollection of facts."
        ),
    },
    {
        "id": "code_gen",
        "label": "Write a small function",
        "prompt": (
            "Write a Python function called `dedupe_preserve_order` that takes a "
            "list and returns a new list with duplicates removed, keeping the "
            "first occurrence and original order. No explanation, just the code."
        ),
    },
    {
        "id": "extraction",
        "label": "Extract structured data",
        "prompt": (
            "Extract the name, email, and requested date as JSON from this "
            "message. Only output valid JSON, nothing else:\n\n"
            "\"Hi, this is Priya Nair, reaching out about rescheduling our call "
            "to next Thursday the 14th. You can reach me at priya.nair@example.com "
            "if anything changes.\""
        ),
    },
    {
        "id": "reasoning",
        "label": "Multi-step reasoning",
        "prompt": (
            "A store had 84 items. On Monday they sold 1/4 of the stock. On "
            "Tuesday they sold half of what remained. How many items are left? "
            "Show your work briefly, then give the final number on its own line."
        ),
    },
    {
        "id": "email_draft",
        "label": "Draft a professional email",
        "prompt": (
            "Write a short, professional email declining a vendor's meeting "
            "request this week due to being fully booked, while asking to "
            "reschedule for next week. Keep it under 80 words."
        ),
    },
]