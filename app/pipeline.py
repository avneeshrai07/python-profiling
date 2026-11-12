"""End-to-end RAG pipeline wiring: ingest -> chunk -> embed -> index, and
query -> embed -> retrieve -> simulate-generate. No real LLM anywhere."""
import time

from app.chunking import chunk_documents
from app.db import init_db, save_chunks
from app.embeddings import embed_batch
from app.generation import simulate_llm_generate
from app.pdf_ingestion import ingest_from_disk
from app.retrieval import retrieve
from app.vector_store import STORE


def ingest_pipeline(num_dummy_pdfs: int = 12, force_regenerate: bool = False):
    start = time.perf_counter()
    init_db()

    docs, _ = ingest_from_disk(num_dummy_pdfs=num_dummy_pdfs, force_regenerate=force_regenerate)
    doc_chunks = chunk_documents(docs)

    total_chunks = 0
    for doc_id, chunks in doc_chunks.items():
        if not chunks:
            continue
        vectors = embed_batch(chunks)
        STORE.add(vectors, doc_id=doc_id, texts=chunks)
        save_chunks(doc_id, chunks)
        total_chunks += len(chunks)

    elapsed = time.perf_counter() - start
    return {
        "documents_loaded": len(docs),
        "chunks_indexed": total_chunks,
        "elapsed_seconds": elapsed,
    }


def query_pipeline(query: str, top_k: int = 5, max_tokens: int = 80):
    results, retrieval_seconds = retrieve(query, top_k=top_k)
    snippets = [entry.text for entry, _score in results]

    gen_start = time.perf_counter()
    answer = simulate_llm_generate(query, snippets, max_tokens=max_tokens)
    generation_seconds = time.perf_counter() - gen_start

    sources = [
        {
            "doc_id": entry.doc_id,
            "chunk_id": entry.chunk_id,
            "score": score,
            "snippet": entry.text[:200],
        }
        for entry, score in results
    ]

    return {
        "answer": answer,
        "sources": sources,
        "retrieval_seconds": retrieval_seconds,
        "generation_seconds": generation_seconds,
    }
