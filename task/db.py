"""
db.py

Sets up the PostgreSQL connection and creates the prompts table if it
doesn't already exist. Uses psycopg (v3).
"""

from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

from config import settings


def init_db() -> None:
    """Creates the prompts table if it doesn't exist yet. Safe to call every run."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS prompts (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                text TEXT NOT NULL,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


@contextmanager
def get_connection():
    """Yields a psycopg connection with dict-style row access, and commits
    automatically on success."""
    conn = psycopg.connect(settings.connection_string, row_factory=dict_row)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()