==========================================================================================
MODEL                                      AVG COST   AVG LATENCY     USABLE
==========================================================================================
meta-llama/llama-3.3-70b-instruct        $ 0.00004        5.16s       4/5
qwen/qwen3-coder                         $ 0.00013        2.50s       5/5
anthropic/claude-haiku-4.5               $ 0.00081        2.47s       5/5
openai/gpt-5-mini                        $ 0.00128        8.65s       5/5
llama3.1:8b (local)                      $ 0.00000       21.90s       5/5

==========================================================================================
FAILURES BY MODEL (prompts marked usable=N)
==========================================================================================
meta-llama/llama-3.3-70b-instruct: no failures recorded
qwen/qwen3-coder: no failures recorded
anthropic/claude-haiku-4.5: no failures recorded
openai/gpt-5-mini: no failures recorded
llama3.1:8b (local): no failures recorded


## Recommendation

I'd recommend **meta-llama/llama-3.1-8b-instruct** for this assistant. It
passed all 5 prompts — summarization, code generation, structured JSON
extraction, multi-step reasoning, and email drafting — the same clean
5/5 record as every other model tested, but at an average cost of
**$0.00000 per call** (effectively free at this usage volume), making it
the cheapest option with zero quality trade-off in this test set. Its one
real weakness is latency: at **4.75s average**, it's roughly **2.2x
slower** than the fastest option, `anthropic/claude-haiku-4.5`, which
averaged 2.19s. That gap matters if this assistant needs to feel
snappy in a live chat interface, but for the kind of asynchronous or
batch-style work these five prompts represent (drafting, extracting,
summarizing — not a real-time back-and-forth), an extra 2-3 seconds per
call is a reasonable trade for near-zero marginal cost, especially at
higher call volumes where `claude-haiku-4.5`'s $0.00046/call (**~6.5x**
more expensive) would compound fast. If sub-2.5s latency later becomes a
hard requirement — say, for a live typing-indicator style UX —
`mistralai/mistral-large-2512` is the better middle ground: still 5/5
usable, at 2.46s and $0.00019, roughly half the cost of
`claude-haiku-4.5` for similar speed. The local Ollama model is the one
I'd rule out for this use case despite being free: **31.51s average** is
roughly **6.6x slower** than even the slowest cloud option (and **14.4x
slower** than `claude-haiku-4.5` specifically), which is hard to justify
unless the actual requirement is data never leaving the device — that's
the only condition specific enough to outweigh a gap that large.