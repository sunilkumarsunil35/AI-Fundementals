# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k rag
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/rag/problems.py

"""Retrieval-augmented generation (RAG): answer from your documents, not from the model's memory.

The pipeline is chunk -> retrieve -> prompt with the chunks -> answer with citations. Each step can be
tested on its own, which is exactly how you should test a RAG feature.
"""

import math
import re
from collections import Counter

MODEL = "claude-opus-5-5"


def _words(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def split_documents(docs: dict[str, str], size: int, overlap: int) -> list[dict]:
    """Split each document (in sorted id order) into chunks of `size` words that start `size - overlap`
    words apart, stopping once a chunk reaches the end. Return dicts {"id": "<doc>#<n>", "doc": doc id,
    "text": chunk words joined by spaces}, n counting from 0 within each document."""
    raise NotImplementedError("Your turn: write this one")


def keyword_score(query: str, text: str) -> float:
    """Return the cosine similarity of the word-count vectors of `query` and `text`. Words are runs of
    lower-case letters and digits. 0.0 if either has no words."""
    raise NotImplementedError("Your turn: write this one")


def retrieve(query: str, chunks: list[dict], k: int) -> list[dict]:
    """Return the k chunks with the highest keyword_score for `query`, best first, ties broken by chunk
    id. Leave out chunks that score 0."""
    raise NotImplementedError("Your turn: write this one")


def build_rag_prompt(question: str, chunks: list[dict]) -> str:
    """Build the prompt: "Answer using only the documents below. Cite each fact with its id in square
    brackets, like [doc#0]. If the documents don't contain the answer, say "I don't know"." then each
    chunk as <document id="ID">TEXT</document> on its own line, then <question>QUESTION</question>."""
    raise NotImplementedError("Your turn: write this one")


def answer_with_rag(client, question: str, chunks: list[dict], k: int) -> tuple[str, list[str]]:
    """Retrieve the top k chunks, send build_rag_prompt(...) to Claude (model MODEL, max_tokens 1024) and
    return (answer text, sorted unique ids cited in square brackets in the answer)."""
    raise NotImplementedError("Your turn: write this one")
