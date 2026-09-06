# Comparison: Raw SQL vs. LangChain PGVector

Two working implementations of the same search functionality exist in this
project — `search.py` (hand-written SQL via psycopg) and `search_langchain.py`
(LangChain's `PGVector` vector store). Both were tested against the same
15 chunks (`data/chunk_sets/`) and confirmed to retrieve overlapping results
for the same query (`tests/test_search_langchain.py::test_langchain_matches_raw_sql_sources`).

## What's different

**Storage**: `search.py` writes to one table (`chunks`) with an explicit,
documented schema (`db.py`). `search_langchain.py` writes to LangChain's own
tables (`langchain_pg_collection`, `langchain_pg_embedding`), created and
managed automatically — the schema is not something this project defines
or controls directly.

**The actual query**: `search.py`'s SQL is fully visible and editable —
the exact `WHERE`/`ORDER BY` clauses are in this codebase, and `sql_used`
in the response even shows the literal query that ran (see `search()`'s
`readable_sql` construction). `search_langchain.py` hides this behind
`similarity_search_with_score()` — the underlying SQL