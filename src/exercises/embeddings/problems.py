# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k embeddings
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/embeddings/problems.py

"""Embeddings and similarity: meaning as a vector of numbers.

An embedding model maps text to a vector so that similar meanings point in similar directions.
Semantic search, RAG, de-duplicating bug reports and clustering test failures all come down to the
few functions here.
"""

import math


def dot(a: list[float], b: list[float]) -> float:
    """Return the dot product of two vectors of the same length."""
    raise NotImplementedError("Your turn: write this one")


def norm(v: list[float]) -> float:
    """Return the length (L2 norm) of vector `v`."""
    raise NotImplementedError("Your turn: write this one")


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Return the cosine of the angle between `a` and `b`: dot(a, b) / (|a| * |b|). Return 0.0 if
    either vector is all zeros."""
    raise NotImplementedError("Your turn: write this one")


def normalize(v: list[float]) -> list[float]:
    """Return `v` scaled to length 1. A zero vector stays all zeros."""
    raise NotImplementedError("Your turn: write this one")


def top_k_similar(query: list[float], vectors: dict[str, list[float]], k: int) -> list[str]:
    """Return the ids of the k vectors most cosine-similar to `query`, best first. Break ties by id in
    alphabetical order."""
    raise NotImplementedError("Your turn: write this one")
