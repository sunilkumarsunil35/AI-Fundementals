# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k nlp
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/nlp/practice.py

"""Text practice: token budgets, chunking for RAG, string similarity and how BPE builds a vocabulary."""

import math
import re
from collections import Counter


def estimate_tokens(text: str) -> int:
    """Estimate how many tokens `text` costs with the rule of thumb of about 4 characters per token,
    rounded up. Empty text is 0 tokens."""
    raise NotImplementedError("Your turn: write this one")


def sentence_split(text: str) -> list[str]:
    """Split `text` into sentences after ".", "!" or "?" followed by whitespace. Strip each sentence and
    drop empty ones."""
    raise NotImplementedError("Your turn: write this one")


def remove_stopwords(tokens: list[str], stopwords: set[str]) -> list[str]:
    """Return the tokens that are not in `stopwords` (compare in lower case), keeping order."""
    raise NotImplementedError("Your turn: write this one")


def jaccard(a: str, b: str) -> float:
    """Return the Jaccard similarity of the sets of lower-case words in `a` and `b` (split on
    whitespace): size of the intersection / size of the union. Two empty strings give 1.0."""
    raise NotImplementedError("Your turn: write this one")


def edit_distance(a: str, b: str) -> int:
    """Return the Levenshtein distance: the fewest single-character inserts, deletes or substitutions
    that turn `a` into `b`."""
    raise NotImplementedError("Your turn: write this one")


def chunk_words(text: str, size: int, overlap: int) -> list[str]:
    """Split `text` into chunks of `size` words, where each chunk starts `size - overlap` words after the
    previous one. Stop once a chunk reaches the last word. Join each chunk's words with single spaces."""
    raise NotImplementedError("Your turn: write this one")


def bpe_merges(words: list[str], num_merges: int) -> list[tuple[str, str]]:
    """Learn byte-pair-encoding merges. Start with every word as a list of characters. Repeat
    `num_merges` times: count every adjacent pair of symbols across all words, pick the most frequent
    pair (the alphabetically smallest on a tie), and merge every occurrence of it into one symbol.
    Stop early if no pairs are left. Return the merges in the order learned."""
    raise NotImplementedError("Your turn: write this one")
