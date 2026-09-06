from models import SearchRequest
from search import search
from search_langchain import search_langchain

QUERY = "how do I reset my password"
K = 5


def test_langchain_returns_results():
    results = search_langchain(QUERY, k=K)
    assert len(results) > 0


def test_langchain_matches_raw_sql_sources():
    """
    Correctness comparison (not duplicate of test_search.py): both paths should
    retrieve overlapping underlying chunks, proving LangChain's PGVector wrapper
    and the hand-written SQL are searching equivalent data with equivalent logic.

    Requires both `chunks` (raw SQL) and LangChain's own collection table to be
    loaded from the same source chunk sets — see the note in search_langchain.py
    about loading the same data into both.
    """
    raw_result = search(SearchRequest(query=QUERY, k=K))
    raw_sources = {r.source for r in raw_result.results}

    lc_results = search_langchain(QUERY, k=K)
    lc_sources = {doc.metadata.get("source") for doc, _score in lc_results}

    overlap = raw_sources & lc_sources
    assert len(overlap) > 0, (
        f"No overlap between raw SQL sources {raw_sources} and "
        f"LangChain sources {lc_sources} — check both were loaded from the same chunk sets."
    )