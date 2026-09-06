import psycopg
from psycopg.rows import dict_row

from config import settings


def get_connection():
    """Raw psycopg connection. Use as a context manager: `with get_connection() as conn:`"""
    return psycopg.connect(settings.database_url, row_factory=dict_row)


def init_db():
    """
    Enable pgvector and create the chunks table if it doesn't exist. Run once (task 1).

    Schema (documented explicitly — load_chunks.py and search.py are both written
    against this contract):
        id         SERIAL PRIMARY KEY
        content    TEXT NOT NULL        -- the chunk text
        embedding  VECTOR(embedding_dim) -- the chunk's embedding
        source     TEXT NOT NULL        -- which document this chunk came from
        page       INTEGER              -- page number in the source doc
        metadata   JSONB                -- filterable fields, e.g. {"category": "billing"}

    Note: CREATE EXTENSION requires superuser (or a role with CREATE privilege
    on extensions) on most managed Postgres providers. If this fails with a
    permission error, either:
      (a) ask your DB admin / provider to enable the "vector" extension once, or
      (b) on managed providers (Supabase, RDS, etc.), enable it via their
          dashboard/console instead of via SQL.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            except psycopg.errors.InsufficientPrivilege:
                conn.rollback()
                raise RuntimeError(
                    "Could not enable pgvector: insufficient privileges. "
                    "Ask your DB admin to run `CREATE EXTENSION vector;` once, "
                    "or enable it via your provider's dashboard, then re-run this script."
                )

            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS chunks (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    page INTEGER,
                    metadata JSONB DEFAULT '{{}}'::jsonb,
                    embedding VECTOR({settings.embedding_dim})
                );
            """)

            # HNSW index for cosine distance search (matches the <=> operator used in search.py)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw_idx
                ON chunks USING hnsw (embedding vector_cosine_ops);
            """)

            # Index to support metadata filtering (task 3)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS chunks_metadata_idx
                ON chunks USING gin (metadata);
            """)

        conn.commit()

    print("pgvector enabled, chunks table + indexes ready.")


if __name__ == "__main__":
    init_db()