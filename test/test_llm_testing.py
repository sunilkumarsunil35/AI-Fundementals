import pytest

from common.fake_claude import APIError
from common.target import load

P = load("llm_testing", "problems")


def test_missing_keywords():
    assert P.missing_keywords("Use PyTest fixtures", ["pytest", "fixture", "mock"]) == ["mock"]


def test_run_golden_set():
    def bot(q):
        if q == "boom":
            raise RuntimeError("model down")
        return {"capital of France": "Paris is the capital", "2+2": "five"}.get(q, "")
    cases = [
        {"id": "geo-1", "input": "capital of France", "expected": ["paris"]},
        {"id": "math-1", "input": "2+2", "expected": ["4"]},
        {"id": "err-1", "input": "boom", "expected": []},
    ]
    assert P.run_golden_set(bot, cases) == {"passed": 1, "failed": 2, "failures": ["math-1", "err-1"]}


def test_consistency_rate():
    answers = iter(["Yes", "yes ", "No", "YES", "no"])
    assert P.consistency_rate(lambda p: next(answers), "q", 5) == 0.6


def test_call_with_retry():
    waits = []
    attempts = iter([APIError(529), APIError(429), "ok"])

    def flaky():
        r = next(attempts)
        if isinstance(r, Exception):
            raise r
        return r
    assert P.call_with_retry(flaky, retries=3, base_delay=1, sleep=waits.append) == "ok"
    assert waits == [1, 2]


def test_call_with_retry_gives_up_and_skips_bad_requests():
    waits = []

    def always_429():
        raise APIError(429)
    with pytest.raises(APIError):
        P.call_with_retry(always_429, retries=2, base_delay=0.5, sleep=waits.append)
    assert waits == [0.5, 1.0]

    def bad_request():
        raise APIError(400)
    with pytest.raises(APIError):
        P.call_with_retry(bad_request, retries=5, base_delay=1, sleep=waits.append)
    assert waits == [0.5, 1.0], "a 400 must not be retried"


def test_parse_judge_score():
    assert P.parse_judge_score("Reasoning... <score> 4 </score>") == 4
    assert P.parse_judge_score("SCORE: 2") == 2
    for bad in ["great answer", "<score>9</score>"]:
        with pytest.raises(ValueError):
            P.parse_judge_score(bad)
