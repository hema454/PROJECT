from pydantic import BaseModel


class ChunkIn(BaseModel):
    """A single chunk to load into the database (pre-embedding)."""
    content: str
    source: str          # which document/chunk set this came from
    page: int | None = None
    metadata: dict = {}  # extra filterable fields, e.g. {"category": "billing"}


class SearchRequest(BaseModel):
    query: str
    k: int = 5
    # optional metadata filter, e.g. {"source": "manual.pdf"} or {"category": "billing"}
    filters: dict | None = None


class SearchResult(BaseModel):
    content: str
    source: str
    page: int | None = None
    distance: float


class SearchResponse(BaseModel):
    results: list[SearchResult]
    sql_used: str  # the raw SQL that was actually executed, for comparison in task 4