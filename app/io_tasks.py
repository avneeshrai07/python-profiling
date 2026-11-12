"""Hard dummy I/O-bound tasks.

These do real disk and database I/O (no mocking) plus a couple of
simulated-latency calls, so I/O profilers / wall-clock vs CPU-time
comparisons have something real to show.
"""
import random
import sqlite3
import time
import uuid
from pathlib import Path

from app.config import CACHE_DIR, SQLITE_PATH
from app.db import init_db


def io_disk_roundtrip(num_files: int = 20, size_kb: int = 512) -> dict:
    """Write N random files to disk, then read them all back."""
    start = time.perf_counter()
    paths: list[Path] = []
    rng = random.Random()
    for _ in range(num_files):
        path = CACHE_DIR / f"blob_{uuid.uuid4().hex}.bin"
        path.write_bytes(rng.randbytes(size_kb * 1024))
        paths.append(path)

    total_bytes = 0
    for path in paths:
        total_bytes += len(path.read_bytes())

    for path in paths:
        path.unlink(missing_ok=True)

    elapsed = time.perf_counter() - start
    return {"task": "io_disk_roundtrip", "elapsed_seconds": elapsed,
            "detail": {"num_files": num_files, "size_kb": size_kb, "bytes_roundtripped": total_bytes}}


def io_sqlite_hammer(num_rows: int = 5000) -> dict:
    """Insert then query a lot of rows against a real on-disk sqlite db."""
    start = time.perf_counter()
    init_db()
    conn = sqlite3.connect(SQLITE_PATH)
    try:
        now = time.time()
        conn.executemany(
            "INSERT INTO bench_rows (payload, created_at) VALUES (?, ?)",
            [(f"row-{i}-{uuid.uuid4().hex}", now) for i in range(num_rows)],
        )
        conn.commit()

        cur = conn.execute("SELECT COUNT(*) FROM bench_rows")
        count = cur.fetchone()[0]

        cur = conn.execute("SELECT payload FROM bench_rows ORDER BY id DESC LIMIT 100")
        _ = cur.fetchall()

        conn.execute("DELETE FROM bench_rows")
        conn.commit()
    finally:
        conn.close()

    elapsed = time.perf_counter() - start
    return {"task": "io_sqlite_hammer", "elapsed_seconds": elapsed,
            "detail": {"num_rows": num_rows, "rows_in_table_at_peak": count}}


def io_simulated_network_calls(num_calls: int = 10, min_delay: float = 0.05, max_delay: float = 0.3) -> dict:
    """Blocking sleeps with jitter -- stands in for calling an external
    vector DB / reranker / LLM API without actually making any network call."""
    start = time.perf_counter()
    rng = random.Random()
    delays = []
    for _ in range(num_calls):
        d = rng.uniform(min_delay, max_delay)
        time.sleep(d)
        delays.append(d)
    elapsed = time.perf_counter() - start
    return {"task": "io_simulated_network_calls", "elapsed_seconds": elapsed,
            "detail": {"num_calls": num_calls, "total_simulated_delay": sum(delays)}}


def io_pdf_batch_read(limit: int | None = None) -> dict:
    """Real file I/O + real PDF parsing CPU work, combined -- a 'mixed' task."""
    from app.pdf_ingestion import ensure_dummy_pdfs, load_all_pdfs

    start = time.perf_counter()
    ensure_dummy_pdfs()
    docs = load_all_pdfs(limit=limit)
    total_chars = sum(len(d.text) for d in docs)
    elapsed = time.perf_counter() - start
    return {"task": "io_pdf_batch_read", "elapsed_seconds": elapsed,
            "detail": {"documents_read": len(docs), "total_characters": total_chars}}


TASKS = {
    "disk": io_disk_roundtrip,
    "sqlite": io_sqlite_hammer,
    "network": io_simulated_network_calls,
    "pdf_batch": io_pdf_batch_read,
}


def run(name: str, **kwargs) -> dict:
    if name not in TASKS:
        raise KeyError(f"unknown io task '{name}', choices: {list(TASKS)}")
    return TASKS[name](**kwargs)
