from pytest import approx

from common.target import load

P = load("rag", "problems")

DOCS = {
    "refunds": "Refunds are issued within 5 days of a return. Contact support for late refunds.",
    "shipping": "Standard shipping takes 3 days. Express shipping takes 1 day.",
}


def test_split_documents():
    chunks = P.split_documents({"b": "one two three four five", "a": "x y"}, 3, 1)
    assert chunks == [
        {"id": "a#0", "doc": "a", "text": "x y"},
        {"id": "b#0", "doc": "b", "text": "one two three"},
        {"id": "b#1", "doc": "b", "text": "three four five"},
    ]


def test_keyword_score():
    assert P.keyword_score("express shipping", "Express shipping takes 1 day.") == approx(2 / (2 ** 0.5 * 5 ** 0.5))
    assert P.keyword_score("", "anything") == 0.0


def test_retrieve():
    chunks = P.split_documents(DOCS, 8, 2)
    top = P.retrieve("how long does express shipping take", chunks, 2)
    assert [c["id"] for c in top] == ["shipping#0", "shipping#1"]
    assert all(c["doc"] == "shipping" for c in top)
    assert P.retrieve("zebra", chunks, 3) == []


def test_build_rag_prompt():
    prompt = P.build_rag_prompt("How fast?", [{"id": "shipping#0", "doc": "shipping", "text": "3 days"}])
    lines = prompt.splitlines()
    assert lines[0].startswith("Answer using only the documents below.") and "I don't know" in lines[0]
    assert lines[1] == '<document id="shipping#0">3 days</document>'
    assert lines[2] == "<question>How fast?</question>"


def test_answer_with_rag(fake_claude):
    chunks = P.split_documents(DOCS, 8, 2)
    client = fake_claude(["Express takes 1 day [shipping#1], standard 3 days [shipping#0][shipping#1]."])
    text, cited = P.answer_with_rag(client, "express shipping time", chunks, 2)
    assert cited == ["shipping#0", "shipping#1"]
    assert '<document id="shipping#1">' in client.last_prompt()
    assert "refunds#0" not in client.last_prompt()
