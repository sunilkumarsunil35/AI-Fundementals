"""RAG practice: measuring retrieval, checking citations and groundedness, and better ranking."""

import math
import re
from collections import Counter


def _words(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def extract_citations(answer: str) -> list[str]:
    """Return every id cited as [something#number] in `answer`, in order of first appearance, without
    duplicates."""
    seen = []
    for c in re.findall(r"\[([^\[\]]+#\d+)\]", answer):
        if c not in seen:
            seen.append(c)
    return seen


def invalid_citations(answer: str, chunk_ids: list[str]) -> list[str]:
    """Return the cited ids that are not in `chunk_ids` (made-up sources), in order of appearance."""
    # A citation to a chunk you never sent is a hallucination you can catch with a plain assert.
    return [c for c in extract_citations(answer) if c not in chunk_ids]


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    """Return the fraction of `relevant` ids found in the first k retrieved ids."""
    return len(set(retrieved[:k]) & relevant) / len(relevant)


def mean_reciprocal_rank(results: list[list[str]], relevant: list[set[str]]) -> float:
    """For each query, take 1 / (1-based rank of the first relevant id), or 0 if none is retrieved.
    Return the mean over all queries."""
    # MRR rewards putting the right chunk first. Users (and models) read the top result most.
    total = 0.0
    for ranked, rel in zip(results, relevant):
        total += next((1 / r for r, id in enumerate(ranked, 1) if id in rel), 0.0)
    return total / len(results)


def groundedness(answer: str, context: str, threshold: float) -> float:
    """Split `answer` into sentences (after . ! or ? plus whitespace). A sentence is supported if at least
    `threshold` of its words appear in `context` (words: lower-case letters and digits). Return the
    fraction of sentences that are supported (1.0 for an empty answer)."""
    # A cheap hallucination detector. An LLM judge does this better; this one is free and instant.
    ctx = set(_words(context))
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", answer.strip()) if _words(s)]
    if not sentences:
        return 1.0
    supported = sum(1 for s in sentences if sum(w in ctx for w in _words(s)) / len(_words(s)) >= threshold)
    return supported / len(sentences)


def bm25_scores(query: str, docs: list[str], k1: float = 1.5, b: float = 0.75) -> list[float]:
    """Score each doc for `query` with BM25. For each query word w found in the doc:
    idf = ln((N - df + 0.5) / (df + 0.5) + 1), and the term adds
    idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(doc) / avg_len)).
    Words are lower-case letters and digits; lengths count words."""
    # BM25 is the keyword ranking behind most search engines, and still a strong RAG baseline.
    toks = [_words(d) for d in docs]
    n = len(docs)
    avg = sum(len(t) for t in toks) / n
    df = Counter(w for t in toks for w in set(t))
    scores = []
    for t in toks:
        tf = Counter(t)
        s = 0.0
        for w in _words(query):
            if tf[w]:
                idf = math.log((n - df[w] + 0.5) / (df[w] + 0.5) + 1)
                s += idf * tf[w] * (k1 + 1) / (tf[w] + k1 * (1 - b + b * len(t) / avg))
        scores.append(s)
    return scores


def hybrid_rank(keyword: dict[str, float], vector: dict[str, float], alpha: float) -> list[str]:
    """Min-max scale each score dict to 0..1 (all-equal scores become 0), then rank ids by
    alpha * keyword + (1 - alpha) * vector, best first, ties by id. An id missing from one dict scores 0
    there."""
    def scale(d):
        if not d:
            return {}
        lo, hi = min(d.values()), max(d.values())
        return {k: (v - lo) / (hi - lo) if hi > lo else 0.0 for k, v in d.items()}
    kw, vec = scale(keyword), scale(vector)
    ids = set(kw) | set(vec)
    return sorted(ids, key=lambda i: (-(alpha * kw.get(i, 0) + (1 - alpha) * vec.get(i, 0)), i))


def context_budget(chunks: list[dict], max_tokens: int) -> list[dict]:
    """Keep chunks in order while their total estimated tokens (ceil(len(text) / 4) each) fit in
    `max_tokens`; stop at the first one that doesn't fit."""
    kept, used = [], 0
    for c in chunks:
        cost = math.ceil(len(c["text"]) / 4)
        if used + cost > max_tokens:
            break
        kept.append(c)
        used += cost
    return kept
