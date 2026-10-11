import pytest

from common.target import load

P = load("llm_testing", "practice")


def test_judge_prompt():
    p = P.judge_prompt("Q?", "A.", "Must mention X")
    assert p.splitlines()[:3] == ["<question>Q?</question>", "<answer>A.</answer>", "<rubric>Must mention X</rubric>"]
    assert p.endswith("inside <score></score> tags.")


def test_llm_judge(fake_claude):
    client = fake_claude(["Covers it well. <score>5</score>", "no idea"])
    assert P.llm_judge(client, "Q", "A", "R") == 5
    assert "<rubric>R</rubric>" in client.last_prompt()
    with pytest.raises(ValueError):
        P.llm_judge(client, "Q", "A", "R")


def test_regressions():
    same = lambda a, b: 1.0 if a.lower() == b.lower() else 0.0
    base = {"q1": "Paris", "q2": "Four", "q3": "Blue"}
    now = {"q1": "paris", "q2": "Five"}
    assert P.regressions(base, now, same, 0.8) == ["q2", "q3"]


def test_latency_stats():
    assert P.latency_stats([120, 80, 300, 95, 110, 2000, 100, 90, 105, 130]) == {"p50": 105, "p95": 2000, "max": 2000}


def test_run_cost():
    usages = [{"input_tokens": 1000, "output_tokens": 500}, {"input_tokens": 3000, "output_tokens": 500}]
    assert P.run_cost(usages, 4.0, 20.0) == 0.036


def test_caching_client(fake_claude):
    fake = fake_claude(["first", "second"])
    client = P.CachingClient(fake)
    kw = dict(model="m", max_tokens=10, messages=[{"role": "user", "content": "hi"}])
    a = client.messages.create(**kw)
    b = client.messages.create(**kw)
    c = client.messages.create(**{**kw, "max_tokens": 20})
    assert a is b and len(fake.calls) == 2 and c is not a
    assert (client.hits, client.misses) == (1, 2)


def test_ab_compare():
    a = lambda x: x.upper()
    b = lambda x: x
    score = lambda x, out: sum(ch.isupper() for ch in out)
    assert P.ab_compare(a, b, ["abc", "XY", "q"], score) == {"a": 2, "b": 0, "tie": 1}


def test_assert_length():
    P.assert_length("one two three", 2, 5)
    with pytest.raises(AssertionError, match="expected 1-2 words, got 3"):
        P.assert_length("one two three", 1, 2)
