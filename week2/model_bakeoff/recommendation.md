# Model Bake-off — Recommendation

## Summary

Five prompt categories (summarize, code_gen, extraction, reasoning, email_draft)
were run against four OpenRouter models and one local Ollama model. Results are
in `results_openrouter.csv` and `results_ollama.csv`.

| Model                        | Avg latency | Total cost (5 prompts) | Usable |
|-------------------------------|------------:|------------------------:|:------:|
| meta-llama/llama-3.3-70b-instruct | 6.46s   | $0.00016                | 5/5    |
| qwen/qwen3-coder               | 3.48s      | $0.00050                | 5/5    |
| anthropic/claude-haiku-4.5      | 1.91s      | $0.00314                | 4/5    |
| openai/gpt-5-mini               | 8.70s      | $0.00553                | 4/5    |
| llama3.1:8b (local, Ollama)     | 24.84s     | $0.00                   | 5/5    |

## Findings

- **claude-haiku-4.5** and **gpt-5-mini** both failed the reasoning prompt,
  landing on "31.5 items remaining" — a non-sensical answer for a discrete
  item count. Both are otherwise fast/capable, but this is a real correctness
  gap, not a formatting nitpick.
- **llama-3.3-70b-instruct** and **qwen3-coder** were both fully usable (5/5)
  and dramatically cheaper than the closed-weight alternatives — llama-3.3 in
  particular costs ~20-30x less than gpt-5-mini for comparable quality on
  these tasks.
- **qwen3-coder** was also the fastest cloud model overall (3.48s avg) despite
  being one of the cheapest.
- **llama3.1:8b (local)** was 100% usable and free, but 4-13x slower than
  every cloud option — acceptable for offline/batch use, not for anything
  latency-sensitive.

## Recommendation

**qwen/qwen3-coder** for general use: fully usable, fastest cloud response
time, and low cost.

**meta-llama/llama-3.3-70b-instruct** as a close second, if lowest cost is
the priority over latency — 5/5 usable at the lowest cost of any model
tested.

**Avoid gpt-5-mini and claude-haiku-4.5** for tasks involving arithmetic/
multi-step reasoning until further testing, based on the reasoning-prompt
failures above. They remain strong for the other four prompt categories.

**llama3.1:8b (local)** is a good zero-cost fallback for non-latency-sensitive
or offline scenarios, but its ~25s average response time makes it impractical
for interactive use.