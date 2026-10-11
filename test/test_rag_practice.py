from pytest import approx

from common.target import load

P = load("rag", "practice")


def test_extract_citations():
    assert P.extract_citations("A [d#1] b [d#0] c [d#1] [not a cite]") == ["d#1", "d#0"]


def test_invalid_citations():
    assert P.invalid_citations("x [d#0] y [d#7]", ["d#0", "d#1"]) == ["d#7"]


def test_recall_at_k():
    assert P.recall_at_k(["a", "x", "b", "y"], {"a", "b", "c"}, 2) == approx(1 / 3)


def test_mean_reciprocal_rank():
    assert P.mean_reciprocal_rank([["x", "a"], ["b"], ["y"]], [{"a"}, {"b"}, {"z"}]) == approx((0.5 + 1 + 0) / 3)


def test_groundedness():
    ctx = "Standard shipping takes 3 days. Express shipping takes 1 day."
    answer = "Express shipping takes 1 day. It is free for members on Mondays."
    assert P.groundedness(answer, ctx, 0.8) == 0.5
    assert P.groundedness("", ctx, 0.8) == 1.0


def test_bm25_scores():
    docs = ["login page error", "cart page", "login login works"]
    s = P.bm25_scores("login error", docs)
    assert s[0] > s[2] > s[1] == 0.0
    assert s[0] == approx(1.3736, abs=1e-3)


def test_hybrid_rank():
    kw = {"a": 10, "b": 0, "c": 5}
    vec = {"a": 0.1, "b": 0.9, "d": 0.5}
    assert P.hybrid_rank(kw, vec, 1.0)[:2] == ["a", "c"]
    assert P.hybrid_rank(kw, vec, 0.0)[0] == "b"
    assert P.hybrid_rank(kw, vec, 0.5) == ["a", "b", "c", "d"], "ties broken by id"


def test_context_budget():
    chunks = [{"text": "x" * 40}, {"text": "y" * 30}, {"text": "z" * 4}]
    assert P.context_budget(chunks, 17) == [chunks[0]]
    assert P.context_budget(chunks, 18) == chunks[:2]
    assert P.context_budget(chunks, 19) == chunks
