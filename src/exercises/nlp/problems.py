# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k nlp
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/nlp/problems.py

"""Text and tokens: how text becomes something a model can count, compare and learn from.

LLMs read tokens, not words, and every RAG system starts by cleaning and chunking text. These are
the classic building blocks, written by hand.
"""

import math
import re
import string
from collections import Counter


def normalize_text(text: str) -> str:
    """Lower-case `text`, remove punctuation and collapse runs of whitespace into single spaces (no
    leading or trailing space)."""
    raise NotImplementedError("Your turn: write this one")


def tokenize(text: str) -> list[str]:
    """Split `text` into lower-case word tokens: runs of letters, digits or apostrophes."""
    raise NotImplementedError("Your turn: write this one")


def ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    """Return every run of n consecutive tokens, as tuples, in order."""
    raise NotImplementedError("Your turn: write this one")


def bag_of_words(docs: list[str]) -> tuple[list[str], list[list[int]]]:
    """Tokenize each document with tokenize(). Return (vocab, vectors): vocab is the sorted list of every
    token seen, and each document's vector counts how often each vocab word appears in it."""
    raise NotImplementedError("Your turn: write this one")


def tf_idf(docs: list[str]) -> list[dict[str, float]]:
    """Return a TF-IDF weight for every token in every document (tokens from tokenize()).
    tf = count of the token in the document / number of tokens in the document.
    idf = ln((1 + N) / (1 + df)) + 1, where N is the number of documents and df how many contain the token.
    Weight = tf * idf."""
    raise NotImplementedError("Your turn: write this one")
