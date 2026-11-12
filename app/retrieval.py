"""Query-time retrieval: embed the query, brute-force search the store."""
import time

from app.embeddings import embed_text
from app.vector_store import STORE


def retrieve(query: str, top_k: int = 5):
    start = time.perf_counter()
    query_vec = embed_text(query)
    results = STORE.search(query_vec, top_k=top_k)
    elapsed = time.perf_counter() - start
    return results, elapsed
