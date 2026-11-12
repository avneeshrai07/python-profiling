"""SQLite-backed metadata store. Used as a deliberately I/O-heavy dependency
for the ingestion pipeline and for the io_tasks benchmark suite."""
import sqlite3
import time
from contextlib import contextmanager

from app.config import SQLITE_PATH


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                doc_id TEXT NOT NULL,
                chunk_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                created_at REAL NOT NULL,
                PRIMARY KEY (doc_id, chunk_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bench_rows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payload TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            """
        )
        conn.commit()


@contextmanager
def get_connection():
    conn = sqlite3.connect(SQLITE_PATH)
    try:
        yield conn
    finally:
        conn.close()


def save_chunks(doc_id: str, chunks: list[str]) -> None:
    now = time.time()
    with get_connection() as conn:
        conn.executemany(
            "INSERT OR REPLACE INTO documents (doc_id, chunk_id, text, created_at) VALUES (?, ?, ?, ?)",
            [(doc_id, i, c, now) for i, c in enumerate(chunks)],
        )
        conn.commit()


def count_documents() -> int:
    with get_connection() as conn:
        cur = conn.execute("SELECT COUNT(DISTINCT doc_id) FROM documents")
        return cur.fetchone()[0]


def reset() -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM documents")
        conn.execute("DELETE FROM bench_rows")
        conn.commit()
