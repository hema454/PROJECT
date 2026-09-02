# LangChain vs Legacy Chain — Comparison

Three things LangChain's abstractions hid from the developer while reimplementing
`legacy_chain.py` as `langchain_chain.py`, and whether each abstraction was worth it.

## 1. The actual HTTP endpoint being called

`legacy_chain.py` explicitly POSTs to Ollama's `/api/generate` endpoint — a raw
completion API, one prompt string in, one string out. `ChatOllama` calls
`/api/chat` instead, a different endpoint with a different wire format (a list of
role/content messages, not a flat prompt). Nothing in `ChatOllama`'s constructor
or the `.ainvoke()` call signals this — you'd only discover it by reading
LangChain's source or watching the request logs, which is exactly how it was
found here (see the `httpx` log lines showing `/api/chat` in `main.py`'s output).

**Worth it?** Yes, cautiously. The endpoint swap didn't change the actual output
(the equivalence check in `main.py` still passes), and `/api/chat` is Ollama's
more actively maintained path going forward. But it's the kind of silent
behavior change that could matter for a model that behaves differently across
its completion vs. chat endpoints — worth a comment in code (already added) so
the next person isn't surprised, and worth re-checking after any Ollama version
bump.

## 2. Message/prompt object construction

`legacy_chain.py` builds one plain Python string and sends it as-is.
`ChatPromptTemplate.from_messages([...])` wraps that same string in a
role-tagged message object before it ever reaches the model, even though this
project only ever uses a single `"human"` turn — no system/assistant messages
in play. The templating, variable substitution, and message-object creation
all happen inside LangChain internals between `PROMPT | llm` and the model
call.

**Worth it?** Marginal for this project's current scope — a single f-string
would do the same job with less indirection. It becomes worth it the moment
this needs multi-turn structure, few-shot examples, or a system prompt,
since `ChatPromptTemplate` handles that cleanly and the legacy string-building
approach would get messy fast. For a single-message extraction task, it's
mostly ceremony today, paid for in exchange for headroom later.

## 3. Error handling and retry internals

`legacy_chain.py` catches `httpx.HTTPError` specifically — you know exactly
what failure modes exist (timeout, connection error, bad status) because
you're the one making the `httpx.AsyncClient` call. `chain.ainvoke()` wraps
whatever `ChatOllama`'s internal client does — its own timeout handling,
possible retry logic, and its own exception types — none of which are visible
from the call site. `langchain_chain.py`'s `extract()` has to catch a bare
`Exception` instead of something specific, because the actual exception type
LangChain might raise isn't part of the visible contract.

**Worth it?** Not clearly, as currently written. Catching `Exception` broadly
is worse practice than the legacy code's specific `httpx.HTTPError` catch —
it can silently swallow bugs unrelated to the model call (e.g. a
`KeyError` in the parser) and misreport them as `ExtractionError("model call
failed")`. This is the one place where LangChain's abstraction cost real
error-handling precision without an obvious corresponding benefit — worth
tightening in a follow-up (e.g. catching LangChain's actual base exception
type once identified) rather than accepting the broad catch long-term.

## Summary

| Hidden thing | Worth it? |
|---|---|
| `/api/generate` → `/api/chat` endpoint switch | Yes, with a comment flagging it |
| Message/prompt object wrapping | Marginal now, pays off with more complex prompts later |
| Error handling internals (broad `except Exception`) | No — should be tightened |