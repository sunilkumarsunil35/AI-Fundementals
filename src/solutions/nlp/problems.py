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
    text = text.lower().translate(str.maketrans("", "", string.punctuation))
    return " ".join(text.split())


def tokenize(text: str) -> list[str]:
    """Split `text` into lower-case word tokens: runs of letters, digits or apostrophes."""
    # A regex tokenizer. Real LLM tokenizers (BPE) split further into sub-word pieces.
    return re.findall(r"[a-z0-9']+", text.lower())


def ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    """Return every run of n consecutive tokens, as tuples, in order."""
    return [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def bag_of_words(docs: list[str]) -> tuple[list[str], list[list[int]]]:
    """Tokenize each document with tokenize(). Return (vocab, vectors): vocab is the sorted list of every
    token seen, and each document's vector counts how often each vocab word appears in it."""
    # Word order is thrown away. "dog bites man" == "man bites dog". Embeddings fix that later.
    tokenized = [tokenize(d) for d in docs]
    vocab = sorted({t for toks in tokenized for t in toks})
    vectors = []
    for toks in tokenized:
        c = Counter(toks)
        vectors.append([c[w] for w in vocab])
    return vocab, vectors


def tf_idf(docs: list[str]) -> list[dict[str, float]]:
    """Return a TF-IDF weight for every token in every document (tokens from tokenize()).
    tf = count of the token in the document / number of tokens in the document.
    idf = ln((1 + N) / (1 + df)) + 1, where N is the number of documents and df how many contain the token.
    Weight = tf * idf."""
    # Words in every document ("the") get a low idf; rare, specific words get a high one.
    tokenized = [tokenize(d) for d in docs]
    n = len(docs)
    df = Counter(t for toks in tokenized for t in set(toks))
    out = []
    for toks in tokenized:
        c = Counter(toks)
        out.append({t: (cnt / len(toks)) * (math.log((1 + n) / (1 + df[t])) + 1) for t, cnt in c.items()})
    return out
