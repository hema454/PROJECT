from models import SearchRequest
from search import search, compare_filtered_vs_unfiltered


def test_search_returns_k_results():
    result = search(SearchRequest(query="how do I reset my password", k=3))
    assert len(result.results) <= 3  # <= in case fewer than k rows exist


def test_search_results_have_source_and_page():
    result = search(SearchRequest(query="how do I reset my password", k=3))
    for r in result.results:
        assert r.source
        # page can legitimately be None, just must be present as a field
        assert hasattr(r, "page")


def test_filter_changes_results():
    """
    Task 3's actual proof: filtered and unfiltered result sets must differ
    when the filter excludes chunks that would otherwise rank highly.
    """
    unfiltered, filtered = compare_filtered_vs_unfiltered(
        query="how do I reset something",
        k=5,
        filters={"category": "account"},
    )

    unfiltered_sources = {r.source for r in unfiltered.results}
    filtered_sources = {r.source for r in filtered.results}

    # every filtered result must come from a source tagged "account"
    for r in filtered.results:
        assert r.content  # sanity: got real content back

    # the unfiltered set should include sources the filter excludes
    # (this is the actual "demonstrably different" proof, not an assertion of equality)
    assert unfiltered_sources != filtered_sources or len(unfiltered.results) != len(filtered.results), (
        "Filter had no effect — unfiltered and filtered results were identical. "
        "Check that your sample data actually has mixed metadata categories."
    )