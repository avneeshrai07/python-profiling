"""Hard dummy CPU-bound tasks.

These exist purely as load for profilers (cProfile, py-spy, scalene, ...)
-- they don't model anything real, they just reliably burn CPU in
different patterns (pure-Python loops, recursion, numpy/BLAS, hashing).
"""
import hashlib
import time

import numpy as np


def cpu_matrix_grind(size: int = 300, iterations: int = 5) -> dict:
    """Repeated dense matmuls -- simulates batches of embedding forward passes."""
    start = time.perf_counter()
    rng = np.random.default_rng(0)
    a = rng.standard_normal((size, size)).astype(np.float32)
    b = rng.standard_normal((size, size)).astype(np.float32)
    checksum = 0.0
    for _ in range(iterations):
        c = a @ b
        checksum += float(c.sum())
        a = c / (np.linalg.norm(c) + 1e-6)
    elapsed = time.perf_counter() - start
    return {"task": "cpu_matrix_grind", "elapsed_seconds": elapsed,
            "detail": {"size": size, "iterations": iterations, "checksum": checksum}}


def cpu_prime_sieve(limit: int = 2_000_000) -> dict:
    """Sieve of Eratosthenes -- simulates re-ranking/scoring a candidate set."""
    start = time.perf_counter()
    is_prime = bytearray([1]) * (limit + 1)
    is_prime[0:2] = b"\x00\x00"
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            is_prime[i * i::i] = bytearray(len(is_prime[i * i::i]))
    count = sum(is_prime)
    elapsed = time.perf_counter() - start
    return {"task": "cpu_prime_sieve", "elapsed_seconds": elapsed,
            "detail": {"limit": limit, "primes_found": count}}


def cpu_naive_fibonacci(n: int = 30) -> dict:
    """Deliberately exponential recursive fibonacci -- an intentional hotspot
    for profilers to pinpoint."""
    start = time.perf_counter()

    def fib(k: int) -> int:
        if k < 2:
            return k
        return fib(k - 1) + fib(k - 2)

    result = fib(n)
    elapsed = time.perf_counter() - start
    return {"task": "cpu_naive_fibonacci", "elapsed_seconds": elapsed,
            "detail": {"n": n, "result": result}}


def cpu_sha256_grind(data_size_mb: int = 5, rounds: int = 3) -> dict:
    """Hash a chunk of data repeatedly -- simulates checksumming/validating
    cached embeddings."""
    start = time.perf_counter()
    data = np.random.default_rng(0).bytes(data_size_mb * 1024 * 1024)
    digest = None
    for _ in range(rounds):
        h = hashlib.sha256()
        h.update(data if digest is None else digest)
        digest = h.digest()
        data = digest * (len(data) // len(digest) + 1)
        data = data[:data_size_mb * 1024 * 1024]
    elapsed = time.perf_counter() - start
    return {"task": "cpu_sha256_grind", "elapsed_seconds": elapsed,
            "detail": {"data_size_mb": data_size_mb, "rounds": rounds, "final_digest": digest.hex()}}


TASKS = {
    "matrix": cpu_matrix_grind,
    "primes": cpu_prime_sieve,
    "fibonacci": cpu_naive_fibonacci,
    "sha256": cpu_sha256_grind,
}


def run(name: str, **kwargs) -> dict:
    if name not in TASKS:
        raise KeyError(f"unknown cpu task '{name}', choices: {list(TASKS)}")
    return TASKS[name](**kwargs)
