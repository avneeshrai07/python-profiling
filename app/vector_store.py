"""Brute-force in-memory vector index.

No FAISS/ANN here on purpose: cosine similarity against every row is
O(N*D), which is exactly the kind of CPU-bound hot loop you want available
for profiling as the corpus grows.
"""
from dataclasses import dataclass

import numpy as np

from app.config import EMBEDDING_DIM


@dataclass
class _Entry:
    doc_id: str
    chunk_id: int
    text: str


class VectorStore:
    def __init__(self, dim: int):
        self.dim = dim
        self._vectors = np.zeros((0, dim), dtype=np.float32)
        self._entries: list[_Entry] = []

    def add(self, vectors: np.ndarray, doc_id: str, texts: list[str]) -> None:
        if vectors.shape[0] != len(texts):
            raise ValueError("vectors/texts length mismatch")
        self._vectors = np.vstack([self._vectors, vectors]) if self._vectors.size else vectors.copy()
        self._entries.extend(_Entry(doc_id=doc_id, chunk_id=i, text=t) for i, t in enumerate(texts))

    def search(self, query_vec: np.ndarray, top_k: int = 5):
        if not self._entries:
            return []
        scores = self._vectors @ query_vec  # brute-force dot product over everything
        top_k = min(top_k, len(scores))
        top_idx = np.argpartition(-scores, top_k - 1)[:top_k]
        top_idx = top_idx[np.argsort(-scores[top_idx])]
        return [(self._entries[i], float(scores[i])) for i in top_idx]

    def __len__(self):
        return len(self._entries)

    def reset(self):
        self._vectors = np.zeros((0, self.dim), dtype=np.float32)
        self._entries = []


STORE = VectorStore(dim=EMBEDDING_DIM)
