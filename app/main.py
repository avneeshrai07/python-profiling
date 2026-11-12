from fastapi import FastAPI

from app.db import init_db
from app.routers import admin, ingest, query, tasks

app = FastAPI(
    title="Simulated RAG/LLM Docker Project",
    version="2.0.0",
    description=(
        "A fake RAG + LLM pipeline (no real model, no network calls to any "
        "LLM) built to generate realistic CPU- and I/O-bound load for "
        "testing profilers, PDF scraping, and load tools like locust."
    ),
)

app.include_router(ingest.router)
app.include_router(query.router)
app.include_router(tasks.router)
app.include_router(admin.router)


@app.on_event("startup")
def _startup():
    init_db()


@app.get("/")
def root():
    return {"message": "Hello World", "see": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/cpu-bound")
def cpu_bound():
    """Kept from the original prototype for backwards compatibility."""
    result = sum(i * i for i in range(10 ** 6))
    return {"result": result}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8005, reload=True)
