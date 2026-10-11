"""Embeddings and similarity: meaning as a vector of numbers.

An embedding model maps text to a vector so that similar meanings point in similar directions.
Semantic search, RAG, de-duplicating bug reports and clustering test failures all come down to the
few functions here.
"""

import math


def dot(a: list[float], b: list[float]) -> float:
    """Return the dot product of two vectors of the same length."""
    return sum(x * y for x, y in zip(a, b))


def norm(v: list[float]) -> float:
    """Return the length (L2 norm) of vector `v`."""
    return math.sqrt(sum(x * x for x in v))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Return the cosine of the angle between `a` and `b`: dot(a, b) / (|a| * |b|). Return 0.0 if
    either vector is all zeros."""
    # 1 = same direction (same meaning), 0 = unrelated, -1 = opposite. Length is ignored.
    na, nb = norm(a), norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return dot(a, b) / (na * nb)


def normalize(v: list[float]) -> list[float]:
    """Return `v` scaled to length 1. A zero vector stays all zeros."""
    # Once vectors are normalised, cosine similarity is just the dot product: faster search.
    n = norm(v)
    return [x / n for x in v] if n else [0.0] * len(v)


def top_k_similar(query: list[float], vectors: dict[str, list[float]], k: int) -> list[str]:
    """Return the ids of the k vectors most cosine-similar to `query`, best first. Break ties by id in
    alphabetical order."""
    ranked = sorted(vectors, key=lambda i: (-cosine_similarity(query, vectors[i]), i))
    return ranked[:k]
