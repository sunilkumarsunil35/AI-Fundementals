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
    chunks = []
    for doc_id in sorted(docs):
        words = docs[doc_id].split()
        for n, start in enumerate(range(0, len(words), size - overlap)):
            chunks.append({"id": f"{doc_id}#{n}", "doc": doc_id, "text": " ".join(words[start:start + size])})
            if start + size >= len(words):
                break
    return chunks


def keyword_score(query: str, text: str) -> float:
    """Return the cosine similarity of the word-count vectors of `query` and `text`. Words are runs of
    lower-case letters and digits. 0.0 if either has no words."""
    # A stand-in for an embedding model, so retrieval works offline. Swap in real embeddings later.
    q, t = Counter(_words(query)), Counter(_words(text))
    num = sum(q[w] * t[w] for w in q)
    den = math.sqrt(sum(v * v for v in q.values())) * math.sqrt(sum(v * v for v in t.values()))
    return num / den if den else 0.0


def retrieve(query: str, chunks: list[dict], k: int) -> list[dict]:
    """Return the k chunks with the highest keyword_score for `query`, best first, ties broken by chunk
    id. Leave out chunks that score 0."""
    scored = [(keyword_score(query, c["text"]), c) for c in chunks]
    scored = [sc for sc in scored if sc[0] > 0]
    scored.sort(key=lambda sc: (-sc[0], sc[1]["id"]))
    return [c for _, c in scored[:k]]


def build_rag_prompt(question: str, chunks: list[dict]) -> str:
    """Build the prompt: "Answer using only the documents below. Cite each fact with its id in square
    brackets, like [doc#0]. If the documents don't contain the answer, say "I don't know"." then each
    chunk as <document id="ID">TEXT</document> on its own line, then <question>QUESTION</question>."""
    # Grounding instructions + ids to cite + an explicit way out ("I don't know") cut hallucinations.
    lines = ['Answer using only the documents below. Cite each fact with its id in square brackets, '
             'like [doc#0]. If the documents don\'t contain the answer, say "I don\'t know".']
    lines += [f'<document id="{c["id"]}">{c["text"]}</document>' for c in chunks]
    lines.append(f"<question>{question}</question>")
    return "\n".join(lines)


def answer_with_rag(client, question: str, chunks: list[dict], k: int) -> tuple[str, list[str]]:
    """Retrieve the top k chunks, send build_rag_prompt(...) to Claude (model MODEL, max_tokens 1024) and
    return (answer text, sorted unique ids cited in square brackets in the answer)."""
    top = retrieve(question, chunks, k)
    response = client.messages.create(model=MODEL, max_tokens=1024,
                                      messages=[{"role": "user", "content": build_rag_prompt(question, top)}])
    text = "".join(b.text for b in response.content if b.type == "text")
    return text, sorted(set(re.findall(r"\[([^\[\]]+#\d+)\]", text)))
