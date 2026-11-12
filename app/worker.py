"""Standalone background process that keeps generating CPU + I/O load.

Useful as a long-running target for py-spy / scalene / cProfile, separate
from the API process. Run directly:

    python -m app.worker

Env vars:
    WORKER_ITERATIONS  number of loop iterations, <=0 means run forever (default 20)
    WORKER_SLEEP       seconds to sleep between iterations (default 0.2)
"""
import os
import random
import time

from app import cpu_tasks, io_tasks
from app.pipeline import ingest_pipeline, query_pipeline

_SAMPLE_QUERIES = [
    "how does retrieval augmented generation reduce latency",
    "what causes a cpu bottleneck in an embedding pipeline",
    "explain chunk overlap and why it matters",
    "why is brute force vector search slow at scale",
]

_JOBS = (
    [lambda: cpu_tasks.run(n) for n in cpu_tasks.TASKS]
    + [lambda: io_tasks.run(n) for n in io_tasks.TASKS]
    + [lambda: query_pipeline(random.choice(_SAMPLE_QUERIES))]
)


def run_once() -> dict:
    job = random.choice(_JOBS)
    start = time.perf_counter()
    result = job()
    elapsed = time.perf_counter() - start
    return {"elapsed_seconds": elapsed, "result": result}


def main():
    iterations = int(os.getenv("WORKER_ITERATIONS", 20))
    sleep_s = float(os.getenv("WORKER_SLEEP", 0.2))

    print("[worker] seeding index via ingest_pipeline()...")
    print(ingest_pipeline())

    i = 0
    while iterations <= 0 or i < iterations:
        info = run_once()
        print(f"[worker] iteration={i} elapsed={info['elapsed_seconds']:.3f}s")
        i += 1
        if sleep_s:
            time.sleep(sleep_s)


if __name__ == "__main__":
    main()
