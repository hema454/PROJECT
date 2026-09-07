"""
Same search as search.py, but using LangChain's PGVector vector store
instead of hand-written SQL. Uses the SAME embedding model
(all-MiniLM-L6-v2) so results are comparable, but stores data in
LangChain's own tables (langchain_pg_collection / langchain_pg_embedding),
separate from the raw `chunks` table search.py uses.

Populate this store first by running load_chunks_langchain.py.
"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector

from config import settings

COLLECTION_NAME = "chunks_langchain"


def _sqlalchemy_url() -> str:
    """
    langchain-postgres needs a SQLAlchemy-style connection string
    (postgresql+psycopg://...), while settings.database_url is a plain
    psycopg-style string (postgresql://...). Convert once, here.
    """
    return settings.database_url.replace("postgresql://", "postgresql+psycopg://", 1)


_embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)

_vectorstore = PGVector(
    embeddings=_embeddings,
    collection_name=COLLECTION_NAME,
    connection=_sqlalchemy_url(),
    use_jsonb=True,
)


def search_langchain(query: str, k: int = 5):
    """
    Returns a list of (Document, score) tuples, same shape as
    LangChain's similarity_search_with_score -- lower score = closer,
    matching the raw SQL path's distance semantics.
    """
    return _vectorstore.similarity_search_with_score(query, k=k)