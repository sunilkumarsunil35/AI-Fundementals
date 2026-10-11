# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k embeddings
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/embeddings/practice.py

"""Embeddings practice: a tiny vector store, diverse results, and grouping near-duplicates."""

import math
from typing import Callable


def _cos(a, b):
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb) if na and nb else 0.0


def euclidean_distance(a: list[float], b: list[float]) -> float:
    """Return the straight-line distance between two vectors."""
    raise NotImplementedError("Your turn: write this one")


def mean_pool(token_vectors: list[list[float]]) -> list[float]:
    """Average a list of same-length token vectors into one vector (element by element)."""
    raise NotImplementedError("Your turn: write this one")


class VectorStore:
    """An in-memory vector database: store vectors with metadata and search them by cosine similarity."""

    def __init__(self):
        """Start empty."""
        raise NotImplementedError("Your turn: write this one")

    def add(self, id: str, vector: list[float], metadata: dict | None = None) -> None:
        """Store `vector` under `id` with optional metadata. Adding an existing id replaces it."""
        raise NotImplementedError("Your turn: write this one")

    def delete(self, id: str) -> bool:
        """Remove `id`. Return True if it was there."""
        raise NotImplementedError("Your turn: write this one")

    def __len__(self) -> int:
        """Return how many vectors are stored."""
        raise NotImplementedError("Your turn: write this one")

    def search(self, query: list[float], k: int, where: dict | None = None) -> list[tuple[str, float]]:
        """Return up to k (id, cosine score) pairs, best first, ties broken by id. If `where` is given,
        only consider items whose metadata has every key/value in `where`."""
        raise NotImplementedError("Your turn: write this one")


def mmr(query: list[float], candidates: dict[str, list[float]], k: int, lambda_: float) -> list[str]:
    """Maximal marginal relevance: pick k ids one at a time. Each step choose the candidate with the
    highest  lambda_ * cos(query, c) - (1 - lambda_) * max(cos(c, s) for s already picked)  (the second
    term is 0 for the first pick). Break ties by id. Return the ids in the order picked."""
    raise NotImplementedError("Your turn: write this one")


def group_similar(vectors: dict[str, list[float]], threshold: float) -> list[list[str]]:
    """Greedy clustering: go through the ids in sorted order. Put each one into the first existing group
    whose first member has cosine similarity >= threshold with it, otherwise start a new group.
    Return the groups."""
    raise NotImplementedError("Your turn: write this one")


def find_duplicates(texts: dict[str, str], embed: Callable[[str], list[float]], threshold: float) -> list[tuple[str, str]]:
    """Embed every text with `embed`, then return every pair of ids (a, b) with a < b whose cosine
    similarity is at least `threshold`, sorted."""
    raise NotImplementedError("Your turn: write this one")
