"""Fake "LLM" generation.

This is a SIMULATION only -- there is no model, no API call, no network
request. It exists to give the rest of the pipeline a plausible
token-by-token latency profile (a tight sleep loop) to point profilers at,
without needing any real inference backend or API key.
"""
import random
import time

_VOCAB = (
    "the system retrieves relevant context before composing a response "
    "based on the indexed chunks shown above the model would normally "
    "attend to each token and predict the next one but here we just "
    "sample filler words to simulate that latency profile for testing"
).split()


def simulate_llm_generate(prompt: str, context_snippets: list[str], max_tokens: int = 80,
                           per_token_delay: float = 0.004) -> str:
    seed = abs(hash((prompt, tuple(context_snippets)))) % (2 ** 32)
    rng = random.Random(seed)

    tokens = []
    for _ in range(max_tokens):
        tokens.append(rng.choice(_VOCAB))
        if per_token_delay:
            time.sleep(per_token_delay)  # simulated token-generation latency

    prefix = "Simulated answer (no real LLM was used): "
    return prefix + " ".join(tokens)
