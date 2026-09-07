import pytest

from db import get_connection
from models import SearchRequest
from search import search, compare_filtered_vs_unfiltered


def _db_available() -> bool:
    """
    Best-effort check for a live DB connection, used to skip these tests
    in environments (e.g. CI) where the full stack isn't running, instead
    of letting them crash with a raw connection error.
    """
    try:
        with get_connection():
            pass
        return True
    except Exception:
        return False


requires_db = pytest.mark.skipif(
    not _db_available(),
    reason="Database is not reachable — skipping tests that require a live DB.",
)


@requires_db
def test_search_returns_k_results():
    result = search(SearchRequest(query="how do I reset my password", k=3))
    assert len(result.results) <= 3  # <= in case fewer than k rows exist


@requires_db
def test_search_results_have_source_and_page():
    result = search(SearchRequest(query="how do I reset my password", k=3))
    for r in result.results:
        assert r.source
        # page can legitimately be None, just must be present as a field
        assert hasattr(r, "page")


@requires_db
def test_filter_changes_results():
    """
    Task 3's actual proof: every result returned under the filter must
    genuinely satisfy the filter condition, not merely produce a
    different-looking result set from the unfiltered search.

    SearchResult doesn't carry metadata/category on the object itself, so
    each filtered result's metadata is looked up back in the DB (via
    content + source) and checked directly against the filter dict. This
    replaces the previous `sources differ OR counts differ` check, which
    would still pass even if the filter silently let non-matching rows
    through, as long as the (unfiltered) result set happened to look
    different for any reason.
    """
    filters = {"category": "account"}
    unfiltered, filtered = compare_filtered_vs_unfiltered(
        query="how do I reset something",
        k=5,
        filters=filters,
    )

    assert len(filtered.results) > 0, (
        "Filter excluded all results — nothing to verify. "
        "Check that your sample data has chunks matching this filter."
    )

    with get_connection() as conn:
        with conn.cursor() as cur:
            for r in filtered.results:
                cur.execute(
                    "SELECT metadata FROM chunks WHERE content = %s AND source = %s LIMIT 1",
                    [r.content, r.source],
                )
                row = cur.fetchone()
                assert row is not None, (
                    f"Could not find the chunk back in the DB for source={r.source!r} "
                    "to verify its metadata (content/source may not be a unique key)."
                )
                metadata = row["metadata"]
                for key, value in filters.items():
                    assert metadata.get(key) == value, (
                        f"Filtered result from {r.source} has metadata {metadata}, "
                        f"which does not satisfy filter {filters}"
                    )

    # sanity check: filtering should actually narrow/change something versus
    # the unfiltered set, otherwise the filter may not be wired up at all
    unfiltered_sources = {r.source for r in unfiltered.results}
    filtered_sources = {r.source for r in filtered.results}
    assert unfiltered_sources != filtered_sources or len(unfiltered.results) != len(filtered.results), (
        "Filter had no effect — unfiltered and filtered results were identical. "
        "Check that your sample data actually has mixed metadata categories."
    )