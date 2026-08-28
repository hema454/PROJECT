from pathlib import Path

import httpx

from config import settings
from prompts import PROMPT_VERSIONS

CHANGELOG_PATH = Path(__file__).resolve().parent / "CHANGELOG.md"


def call_model(prompt: str) -> str:
    
    response = httpx.post(
        settings.openrouter_base_url,
        headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
        json={
            "model": settings.model,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30.0,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def run_all_versions() -> list[dict]:
    
    results = []
    for version in PROMPT_VERSIONS:
        print(f"Running {version['name']}...")
        try:
            actual = call_model(version["prompt"]).strip()
        except httpx.HTTPStatusError as e:
            actual = f"[API error] {e.response.status_code} — {e.response.text}"
        results.append({**version, "actual": actual})
    return results


def write_changelog(results: list[dict]) -> None:
    
    lines = ["# Prompt Iteration Log — Article Summarization\n"]
    for r in results:
        lines.append(f"## {r['name']}")
        lines.append(f"**Prompt:**\n```\n{r['prompt'].strip()}\n```")
        lines.append(f"**Changed:** {r['changed']}")
        lines.append(f"**Expected:** {r['expected']}")
        lines.append(f"**Actual:** {r['actual']}")
        lines.append("")  # blank line between versions

    CHANGELOG_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nCHANGELOG.md written to {CHANGELOG_PATH}")


def main():
    print(f"Testing model: {settings.model}\n")
    results = run_all_versions()
    write_changelog(results)


if __name__ == "__main__":
    main()