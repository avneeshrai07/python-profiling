"""Sliding-window word chunking. Pure-Python string/list work -- CPU-bound
and deliberately unoptimized so profilers have something to find."""
from app.config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP


def chunk_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    if not words:
        return []

    chunks = []
    step = max(chunk_size - overlap, 1)
    for start in range(0, len(words), step):
        window = words[start:start + chunk_size]
        if not window:
            break
        chunks.append(" ".join(window))
        if start + chunk_size >= len(words):
            break
    return chunks


def chunk_documents(docs, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP):
    """docs: list of app.pdf_ingestion.Document -> dict[doc_id] -> list[str] chunks"""
    out = {}
    for doc in docs:
        out[doc.doc_id] = chunk_text(doc.text, chunk_size=chunk_size, overlap=overlap)
    return out
