"""Simulated embedding model.

There is NO real model here -- just feature hashing followed by a fixed
random projection matrix, done with numpy so the matmul is real CPU work
whose cost scales with batch size, standing in for an embedding model's
forward pass for profiling purposes.
"""
import numpy as np

from app.config import FEATURE_DIM, EMBEDDING_DIM, PROJECTION_SEED

_rng = np.random.default_rng(PROJECTION_SEED)
_PROJECTION = _rng.standard_normal((FEATURE_DIM, EMBEDDING_DIM)).astype(np.float32)


def _hash_features(text: str) -> np.ndarray:
    vec = np.zeros(FEATURE_DIM, dtype=np.float32)
    if len(text) < 2:
        return vec
    for i in range(len(text) - 1):
        bigram = text[i:i + 2]
        idx = hash(bigram) % FEATURE_DIM
        vec[idx] += 1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


def embed_text(text: str) -> np.ndarray:
    feats = _hash_features(text)
    vec = feats @ _PROJECTION
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


def embed_batch(texts: list[str]) -> np.ndarray:
    """Batched version -- one bigger matmul instead of N small ones."""
    feats = np.stack([_hash_features(t) for t in texts]) if texts else np.zeros((0, FEATURE_DIM), dtype=np.float32)
    vecs = feats @ _PROJECTION
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vecs / norms
