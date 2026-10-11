# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k rag
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/rag/practice.py

"""RAG practice: measuring retrieval, checking citations and groundedness, and better ranking."""

import math
import re
from collections import Counter


def _words(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def extract_citations(answer: str) -> list[str]:
    """Return every id cited as [something#number] in `answer`, in order of first appearance, without
    duplicates."""
    raise NotImplementedError("Your turn: write this one")


def invalid_citations(answer: str, chunk_ids: list[str]) -> list[str]:
    """Return the cited ids that are not in `chunk_ids` (made-up sources), in order of appearance."""
    raise NotImplementedError("Your turn: write this one")


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    """Return the fraction of `relevant` ids found in the first k retrieved ids."""
    raise NotImplementedError("Your turn: write this one")


def mean_reciprocal_rank(results: list[list[str]], relevant: list[set[str]]) -> float:
    """For each query, take 1 / (1-based rank of the first relevant id), or 0 if none is retrieved.
    Return the mean over all queries."""
    raise NotImplementedError("Your turn: write this one")


def groundedness(answer: str, context: str, threshold: float) -> float:
    """Split `answer` into sentences (after . ! or ? plus whitespace). A sentence is supported if at least
    `threshold` of its words appear in `context` (words: lower-case letters and digits). Return the
    fraction of sentences that are supported (1.0 for an empty answer)."""
    raise NotImplementedError("Your turn: write this one")


def bm25_scores(query: str, docs: list[str], k1: float = 1.5, b: float = 0.75) -> list[float]:
    """Score each doc for `query` with BM25. For each query word w found in the doc:
    idf = ln((N - df + 0.5) / (df + 0.5) + 1), and the term adds
    idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(doc) / avg_len)).
    Words are lower-case letters and digits; lengths count words."""
    raise NotImplementedError("Your turn: write this one")


def hybrid_rank(keyword: dict[str, float], vector: dict[str, float], alpha: float) -> list[str]:
    """Min-max scale each score dict to 0..1 (all-equal scores become 0), then rank ids by
    alpha * keyword + (1 - alpha) * vector, best first, ties by id. An id missing from one dict scores 0
    there."""
    raise NotImplementedError("Your turn: write this one")


def context_budget(chunks: list[dict], max_tokens: int) -> list[dict]:
    """Keep chunks in order while their total estimated tokens (ceil(len(text) / 4) each) fit in
    `max_tokens`; stop at the first one that doesn't fit."""
    raise NotImplementedError("Your turn: write this one")
