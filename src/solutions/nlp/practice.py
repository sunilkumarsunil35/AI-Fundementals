"""Text practice: token budgets, chunking for RAG, string similarity and how BPE builds a vocabulary."""

import math
import re
from collections import Counter


def estimate_tokens(text: str) -> int:
    """Estimate how many tokens `text` costs with the rule of thumb of about 4 characters per token,
    rounded up. Empty text is 0 tokens."""
    # Good enough for a budget check. For an exact count, call client.messages.count_tokens().
    return math.ceil(len(text) / 4)


def sentence_split(text: str) -> list[str]:
    """Split `text` into sentences after ".", "!" or "?" followed by whitespace. Strip each sentence and
    drop empty ones."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def remove_stopwords(tokens: list[str], stopwords: set[str]) -> list[str]:
    """Return the tokens that are not in `stopwords` (compare in lower case), keeping order."""
    return [t for t in tokens if t.lower() not in stopwords]


def jaccard(a: str, b: str) -> float:
    """Return the Jaccard similarity of the sets of lower-case words in `a` and `b` (split on
    whitespace): size of the intersection / size of the union. Two empty strings give 1.0."""
    sa, sb = set(a.lower().split()), set(b.lower().split())
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb)


def edit_distance(a: str, b: str) -> int:
    """Return the Levenshtein distance: the fewest single-character inserts, deletes or substitutions
    that turn `a` into `b`."""
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def chunk_words(text: str, size: int, overlap: int) -> list[str]:
    """Split `text` into chunks of `size` words, where each chunk starts `size - overlap` words after the
    previous one. Stop once a chunk reaches the last word. Join each chunk's words with single spaces."""
    # The overlap keeps a sentence that straddles a boundary readable in at least one chunk.
    words = text.split()
    step = size - overlap
    chunks = []
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start:start + size]))
        if start + size >= len(words):
            break
    return chunks


def bpe_merges(words: list[str], num_merges: int) -> list[tuple[str, str]]:
    """Learn byte-pair-encoding merges. Start with every word as a list of characters. Repeat
    `num_merges` times: count every adjacent pair of symbols across all words, pick the most frequent
    pair (the alphabetically smallest on a tie), and merge every occurrence of it into one symbol.
    Stop early if no pairs are left. Return the merges in the order learned."""
    # This is how GPT-style and Claude-style tokenizers get sub-word tokens like "ing" or "test".
    corpus = [list(w) for w in words]
    merges = []
    for _ in range(num_merges):
        pairs = Counter()
        for symbols in corpus:
            pairs.update(zip(symbols, symbols[1:]))
        if not pairs:
            break
        best = min(pairs, key=lambda p: (-pairs[p], p))
        merges.append(best)
        merged = best[0] + best[1]
        for k, symbols in enumerate(corpus):
            out, i = [], 0
            while i < len(symbols):
                if i + 1 < len(symbols) and (symbols[i], symbols[i + 1]) == best:
                    out.append(merged)
                    i += 2
                else:
                    out.append(symbols[i])
                    i += 1
            corpus[k] = out
    return merges
