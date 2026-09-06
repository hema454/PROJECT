import psycopg
from psycopg.rows import dict_row
from pgvector.psycopg import register_vector

from config import settings


def get_connection():
    conn = psycopg.connect(settings.database_url, row_factory=dict_row)
    register_vector(conn)
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS rag_chunks (
                id SERIAL PRIMARY KEY,
                doc_name TEXT NOT NULL,
                page INT NOT NULL,
                content TEXT NOT NULL,
                embedding VECTOR({settings.embedding_dim})
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS rag_chunks_embedding_idx
            ON rag_chunks USING hnsw (embedding vector_cosine_ops)
            """
        )
        conn.commit()


def insert_chunk(doc_name: str, page: int, content: str, embedding: list[float]):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO rag_chunks (doc_name, page, content, embedding) VALUES (%s, %s, %s, %s)",
            (doc_name, page, content, embedding),
        )
        conn.commit()


def similarity_search(query_embedding: list[float], top_k: int):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT doc_name, page, content, embedding <=> %s::vector AS distance
            FROM rag_chunks
            ORDER BY distance ASC
            LIMIT %s
            """,
            (query_embedding, top_k),
        ).fetchall()
        return rows