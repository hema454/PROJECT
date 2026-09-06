import json

from config import settings
from db import get_connection
from embeddings import embed_text
from models import SearchRequest, SearchResponse, SearchResult


def search(request: SearchRequest) -> SearchResponse:
    """
    Task 2: returns top-k chunks with source and page.
    Task 3: if request.filters is set, applies a metadata filter alongside the vector search.
    """
    query_vector = embed_text(request.query)
    vector_str = str(query_vector)

    where_clause = "WHERE metadata @> %s" if request.filters else ""

    sql = f"""
        SELECT content, source, page, embedding <=> %s AS distance
        FROM chunks
        {where_clause}
        ORDER BY embedding <=> %s
        LIMIT %s
    """.strip()

    # embedding <=> %s appears twice (SELECT + ORDER BY), so vector_str is passed twice
    params = [vector_str]
    if request.filters:
        params.append(json.dumps(request.filters))
    params += [vector_str, request.k]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

    results = [
        SearchResult(
            content=row["content"],
            source=row["source"],
            page=row["page"],
            distance=row["distance"],
        )
        for row in rows
    ]

    # Render the SQL with actual values inlined, for task 4 comparison / task 3 proof
    readable_sql = sql
    for p in params:
        readable_sql = readable_sql.replace("%s", repr(p), 1)

    return SearchResponse(results=results, sql_used=readable_sql)


def compare_filtered_vs_unfiltered(query: str, k: int, filters: dict):
    """
    Task 3: run both searches and print both result sets side by side,
    so the difference is shown, not asserted.
    """
    unfiltered = search(SearchRequest(query=query, k=k, filters=None))
    filtered = search(SearchRequest(query=query, k=k, filters=filters))

    print("=== UNFILTERED RESULTS ===")
    for r in unfiltered.results:
        print(f"  [{r.source} p.{r.page}] dist={r.distance:.4f}  {r.content[:80]}")

    print(f"\n=== FILTERED RESULTS (filters={filters}) ===")
    for r in filtered.results:
        print(f"  [{r.source} p.{r.page}] dist={r.distance:.4f}  {r.content[:80]}")

    unfiltered_set = {r.content for r in unfiltered.results}
    filtered_set = {r.content for r in filtered.results}
    print(f"\nOverlap: {len(unfiltered_set & filtered_set)} of {k} chunks identical")
    print(f"Different: {len(unfiltered_set - filtered_set)} chunks changed due to filter")

    return unfiltered, filtered


if __name__ == "__main__":
    result = search(SearchRequest(query="how do I reset my password", k=settings.default_k))
    print(result.sql_used)
    for r in result.results:
        print(f"[{r.source} p.{r.page}] dist={r.distance:.4f}  {r.content[:80]}")