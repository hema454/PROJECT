from contextlib import asynccontextmanager

from fastapi import FastAPI
from models import SearchResponse



from db import init_db
from models import SearchRequest, SearchResponse
from search import search


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield  # app runs while paused here
    # (nothing needed on shutdown for this app)


app = FastAPI(title="pgvector search", lifespan=lifespan)


@app.post("/search", response_model=SearchResponse)
def search_endpoint(request: SearchRequest) -> SearchResponse:
    """
    Task 2: returns top-k chunks with source and page.
    Task 3: pass `filters` in the request body to apply a metadata filter
            alongside the vector search, e.g. {"category": "billing"}.
    """
    return search(request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)