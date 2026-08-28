"""
store.py

CRUD functions for the prompt store, backed by PostgreSQL. This is the
layer your other scripts import from — they never write SQL directly.
"""

from db import get_connection


def add_prompt(name: str, text: str, tags: str = "") -> None:
    """Adds a new prompt. Raises psycopg.errors.UniqueViolation if name
    already exists — use update_prompt() to change an existing one."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO prompts (name, text, tags) VALUES (%s, %s, %s)",
            (name, text, tags),
        )


def get_prompt(name: str) -> dict | None:
    """Fetches one prompt by name. Returns None if not found."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM prompts WHERE name = %s", (name,)
        ).fetchone()
        return dict(row) if row else None


def list_prompts(tag: str | None = None) -> list[dict]:
    """Lists all prompts, optionally filtered by tag."""
    with get_connection() as conn:
        if tag:
            rows = conn.execute(
                "SELECT * FROM prompts WHERE tags LIKE %s ORDER BY updated_at DESC",
                (f"%{tag}%",),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM prompts ORDER BY updated_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]


def update_prompt(name: str, text: str) -> bool:
    """Updates an existing prompt's text. Returns True if a row was updated,
    False if no prompt with that name exists."""
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE prompts SET text = %s, updated_at = CURRENT_TIMESTAMP WHERE name = %s",
            (text, name),
        )
        return cursor.rowcount > 0


def delete_prompt(name: str) -> bool:
    """Deletes a prompt by name. Returns True if a row was deleted."""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM prompts WHERE name = %s", (name,))
        return cursor.rowcount > 0