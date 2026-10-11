"""Embeddings practice: a tiny vector store, diverse results, and grouping near-duplicates."""

import math
from typing import Callable


def _cos(a, b):
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb) if na and nb else 0.0


def euclidean_distance(a: list[float], b: list[float]) -> float:
    """Return the straight-line distance between two vectors."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def mean_pool(token_vectors: list[list[float]]) -> list[float]:
    """Average a list of same-length token vectors into one vector (element by element)."""
    # One common way to turn per-token vectors into a single sentence embedding.
    n = len(token_vectors)
    return [sum(col) / n for col in zip(*token_vectors)]


class VectorStore:
    """An in-memory vector database: store vectors with metadata and search them by cosine similarity."""

    def __init__(self):
        """Start empty."""
        self._items = {}

    def add(self, id: str, vector: list[float], metadata: dict | None = None) -> None:
        """Store `vector` under `id` with optional metadata. Adding an existing id replaces it."""
        self._items[id] = (vector, metadata or {})

    def delete(self, id: str) -> bool:
        """Remove `id`. Return True if it was there."""
        return self._items.pop(id, None) is not None

    def __len__(self) -> int:
        """Return how many vectors are stored."""
        return len(self._items)

    def search(self, query: list[float], k: int, where: dict | None = None) -> list[tuple[str, float]]:
        """Return up to k (id, cosine score) pairs, best first, ties broken by id. If `where` is given,
        only consider items whose metadata has every key/value in `where`."""
        # Metadata filters ("only docs for release 2.3") are what make a vector DB useful in practice.
        hits = []
        for id, (vec, meta) in self._items.items():
            if where and any(meta.get(key) != value for key, value in where.items()):
                continue
            hits.append((id, _cos(query, vec)))
        hits.sort(key=lambda h: (-h[1], h[0]))
        return hits[:k]


def mmr(query: list[float], candidates: dict[str, list[float]], k: int, lambda_: float) -> list[str]:
    """Maximal marginal relevance: pick k ids one at a time. Each step choose the candidate with the
    highest  lambda_ * cos(query, c) - (1 - lambda_) * max(cos(c, s) for s already picked)  (the second
    term is 0 for the first pick). Break ties by id. Return the ids in the order picked."""
    # Plain top-k can return five copies of the same paragraph. MMR trades a bit of relevance for variety.
    picked = []
    left = dict(candidates)
    while left and len(picked) < k:
        def score(i):
            redundancy = max((_cos(left[i], candidates[s]) for s in picked), default=0.0)
            return lambda_ * _cos(query, left[i]) - (1 - lambda_) * redundancy
        best = min(left, key=lambda i: (-score(i), i))
        picked.append(best)
        del left[best]
    return picked


def group_similar(vectors: dict[str, list[float]], threshold: float) -> list[list[str]]:
    """Greedy clustering: go through the ids in sorted order. Put each one into the first existing group
    whose first member has cosine similarity >= threshold with it, otherwise start a new group.
    Return the groups."""
    groups = []
    for id in sorted(vectors):
        for g in groups:
            if _cos(vectors[g[0]], vectors[id]) >= threshold:
                g.append(id)
                break
        else:
            groups.append([id])
    return groups


def find_duplicates(texts: dict[str, str], embed: Callable[[str], list[float]], threshold: float) -> list[tuple[str, str]]:
    """Embed every text with `embed`, then return every pair of ids (a, b) with a < b whose cosine
    similarity is at least `threshold`, sorted."""
    # SDET use: "is this new bug report a duplicate of an open one?" Pass Claude-compatible
    # embeddings (for example Voyage AI) in real life; the tests pass a simple word-count embedder.
    vecs = {i: embed(t) for i, t in texts.items()}
    ids = sorted(vecs)
    return [(a, b) for x, a in enumerate(ids) for b in ids[x + 1:] if _cos(vecs[a], vecs[b]) >= threshold]
