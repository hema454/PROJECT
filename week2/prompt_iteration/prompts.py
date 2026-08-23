

ARTICLE = """
The city council approved a $4.5M budget for downtown road repairs on Wednesday.
The project will begin in April and is expected to take six months. Officials said
the repairs will affect Main Street, Oak Avenue, and Third Street, with detours
planned during peak construction. Local business owners expressed concern about
reduced foot traffic during the repair period, while the mayor's office said the
long-term infrastructure investment was necessary and overdue.
"""



PROMPT_VERSIONS = [
    {
        "name": "Version 1 (baseline)",
        "prompt": f"""Summarize this article in 3 bullet points.

{ARTICLE}""",
        "changed": "N/A (starting point)",
        "expected": "N/A",
    },
    {
        "name": "Version 2",
        "prompt": f"""Summarize this article in 3 bullet points. Do not include your own opinion.

{ARTICLE}""",
        "changed": 'Added a negative instruction: "Do not include your own opinion."',
        "expected": "AI stops adding opinions entirely.",
    },
    {
        "name": "Version 3",
        "prompt": f"""Summarize this article in exactly 3 bullet points. Each bullet must state only a fact from the article — a specific event, number, or quote. Do not add analysis, commentary, or evaluation.

{ARTICLE}""",
        "changed": "Replaced the vague negative instruction with a positive, concrete rule: each bullet must state a specific fact (event/number/quote).",
        "expected": "AI produces purely factual bullets, no opinion, no hedging phrases.",
    },
    {
        "name": "Version 4",
        "prompt": f"""Summarize the article below in exactly 3 bullet points. Each bullet must state only a fact from the article — a specific event, number, or quote. Do not add analysis, commentary, or evaluation.

<article>
{ARTICLE}
</article>""",
        "changed": "Wrapped the article text in <article> tags to clearly separate instructions from content.",
        "expected": "AI stays more focused on facts within the article, less drift, especially on longer articles.",
    },
    {
        "name": "Version 5",
        "prompt": f"""Summarize the article below in exactly 3 bullet points. Each bullet must state only a fact from the article — a specific event, number, or quote. Do not add analysis, commentary, or evaluation.

Example:
<article>
The city council approved a $2M budget for park renovations on Tuesday. Construction begins in March. Three parks will be affected: Riverside, Oak Hill, and Central.
</article>
Output:
- City council approved a $2M budget for park renovations on Tuesday.
- Construction is set to begin in March.
- Three parks affected: Riverside, Oak Hill, and Central.

Now summarize this article:
<article>
{ARTICLE}
</article>""",
        "changed": "Added a one-shot example showing the exact input/output format.",
        "expected": "AI matches the demonstrated bullet style and length more consistently than V4.",
    },
]