import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "task4"))

from config import settings  # noqa: E402
from db import get_connection  # noqa: E402


def init_variant_table(table_name: str):
    with get_connection() as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                doc_name TEXT NOT NULL,
                page INT NOT NULL,
                content TEXT NOT NULL,
                embedding VECTOR({settings.embedding_dim})
            )
            """
        )
        conn.execute(
            f"""
            CREATE INDEX IF NOT EXISTS {table_name}_embedding_idx
            ON {table_name} USING hnsw (embedding vector_cosine_ops)
            """
        )
        conn.commit()


def insert_variant_chunk(table_name: str, doc_name: str, page: int, content: str, embedding: list[float]):
    with get_connection() as conn:
        conn.execute(
            f"INSERT INTO {table_name} (doc_name, page, content, embedding) VALUES (%s, %s, %s, %s)",
            (doc_name, page, content, embedding),
        )
        conn.commit()


def similarity_search_variant(table_name: str, query_embedding: list[float], top_k: int):
    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT doc_name, page, content, embedding <=> %s::vector AS distance
            FROM {table_name}
            ORDER BY distance ASC
            LIMIT %s
            """,
            (query_embedding, top_k),
        ).fetchall()
        return rows


def drop_table(table_name: str):
    with get_connection() as conn:
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()