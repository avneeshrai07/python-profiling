# Simulated RAG/LLM Docker Project

A fake "real-world" RAG + LLM system with **no real model and no network
calls to any LLM**. Every "AI" step (embedding, retrieval ranking, text
generation) is simulated with deterministic hashing, numpy matmuls, or
sleeps -- just enough to produce realistic CPU-bound and I/O-bound load for
exercising profilers, PDF-scraping code, and load-testing tools.

## Layout

```
app/
  main.py          FastAPI app + routes
  pdf_ingestion.py generates dummy PDFs, parses them back (real I/O + CPU)
  chunking.py      sliding-window text chunking
  embeddings.py    simulated embedding model (feature hashing + random projection)
  vector_store.py  brute-force in-memory cosine similarity index
  retrieval.py     query embedding + search
  generation.py    simulated "LLM" generation (no real model)
  pipeline.py      wires ingest/query end to end
  cpu_tasks.py     hard dummy CPU-bound tasks (matrix, primes, fibonacci, sha256)
  io_tasks.py      hard dummy I/O-bound tasks (disk, sqlite, simulated network, pdf batch)
  worker.py        standalone long-running loop for profiling outside the API process
  db.py            sqlite metadata store
  routers/         /ingest, /query, /tasks, /admin
scripts/generate_dummy_pdfs.py   CLI to (re)build the dummy PDF corpus
```

## Run locally

```bash
python -m venv myvenv && source myvenv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8005 --reload
```

Open http://127.0.0.1:8005/docs for the interactive API.

## Run with Docker

```bash
docker compose up --build
```

This starts an `api` service (port 8005) and a `worker` service that loops
forever generating load -- useful as a separate, steady profiling target.

## Typical flow

```bash
curl -X POST localhost:8005/ingest -H 'content-type: application/json' -d '{"num_dummy_pdfs": 12}'
curl -X POST localhost:8005/query  -H 'content-type: application/json' -d '{"query": "how does retrieval work"}'
curl localhost:8005/tasks/list
curl localhost:8005/tasks/cpu/matrix
curl localhost:8005/tasks/io/sqlite
curl localhost:8005/tasks/mixed
```

## Profiling ideas

- **cProfile** on the worker (finite loop, easy to bound):
  `WORKER_ITERATIONS=5 python -m cProfile -o out.prof -m app.worker`
  then inspect with `snakeviz out.prof` or `pstats`.
- **py-spy** against the running API or worker process:
  `py-spy record -o profile.svg --pid <pid>`
- **scalene** for CPU+memory line-level profiling:
  `scalene -m app.worker`
- **memory_profiler** on `cpu_tasks.cpu_matrix_grind` or `io_tasks.io_disk_roundtrip`
  to see allocation patterns.
- **locust** for API-level load testing:
  `locust -f locustfile.py --host=http://127.0.0.1:8005`
- **PDF scraping models**: swap `app/pdf_ingestion.extract_text_from_pdf` for a
  heavier model (layout parsing, OCR, table extraction) and compare its
  profile against the current pypdf baseline using the same dummy corpus
  in `data/pdfs/` (regenerate/resize it with `python -m scripts.generate_dummy_pdfs --count 50`).

## Why fake everything?

So this can be profiled and stress-tested entirely offline, with no API
keys, no rate limits, and fully reproducible timings -- while still
exercising the same shapes of work (batched linear algebra, disk/db I/O,
blocking waits) a real RAG+LLM service would have.
