"""LLM testing practice: LLM-as-judge, regression checks, latency and cost, caching and A/B comparisons."""

import json
import math
import re
from typing import Callable

MODEL = "claude-opus-5-5"


def judge_prompt(question: str, answer: str, rubric: str) -> str:
    """Build a grading prompt that puts the question, answer and rubric in <question>, <answer> and
    <rubric> tags (one per line, in that order) and ends with: "Think it through, then give a score from
    1 to 5 inside <score></score> tags." """
    return (
        f"<question>{question}</question>\n<answer>{answer}</answer>\n<rubric>{rubric}</rubric>\n"
        "Think it through, then give a score from 1 to 5 inside <score></score> tags."
    )


def llm_judge(client, question: str, answer: str, rubric: str) -> int:
    """Send judge_prompt(...) to Claude (model MODEL, max_tokens 1024) and return the score in the reply.
    Raise ValueError if the reply holds no <score> tag with 1-5."""
    # LLM-as-judge grades free text against a rubric. Validate the judge itself on a few hand-graded
    # examples before trusting it.
    response = client.messages.create(model=MODEL, max_tokens=1024,
                                      messages=[{"role": "user", "content": judge_prompt(question, answer, rubric)}])
    text = "".join(b.text for b in response.content if b.type == "text")
    m = re.search(r"<score>\s*(\d+)\s*</score>", text)
    if not m or not 1 <= int(m.group(1)) <= 5:
        raise ValueError("judge gave no valid score")
    return int(m.group(1))


def regressions(baseline: dict[str, str], current: dict[str, str], similarity: Callable[[str, str], float], threshold: float) -> list[str]:
    """Compare today's answers with the approved baseline answers, id by id. Return the sorted ids that
    are missing from `current` or whose similarity to the baseline is below `threshold`."""
    # Snapshot testing for LLMs: wording may change, meaning may not.
    return sorted(i for i in baseline if i not in current or similarity(baseline[i], current[i]) < threshold)


def latency_stats(durations_ms: list[float]) -> dict:
    """Return {"p50": .., "p95": .., "max": ..} using the nearest-rank percentile: sort the values and
    take the one at position ceil(p/100 * n) (1-based)."""
    s = sorted(durations_ms)
    rank = lambda p: s[max(1, math.ceil(p / 100 * len(s))) - 1]
    return {"p50": rank(50), "p95": rank(95), "max": s[-1]}


def run_cost(usages: list[dict], input_per_mtok: float, output_per_mtok: float) -> float:
    """Each usage dict has "input_tokens" and "output_tokens". Prices are dollars per million tokens.
    Return the total cost in dollars, rounded to 6 decimal places."""
    inp = sum(u["input_tokens"] for u in usages)
    out = sum(u["output_tokens"] for u in usages)
    return round((inp * input_per_mtok + out * output_per_mtok) / 1_000_000, 6)


class CachingClient:
    """Wrap a client so identical messages.create() requests are answered from a cache. Tests that rerun
    the same prompt cost nothing after the first call."""

    def __init__(self, client):
        """Keep `client`, start an empty cache, and expose `self.messages` with a create() method and
        `self.hits` / `self.misses` counters."""
        self._client = client
        self._cache = {}
        self.hits = 0
        self.misses = 0
        self.messages = self

    def create(self, **kwargs):
        """Return the cached response for these exact kwargs, or call the real client and cache it."""
        key = json.dumps(kwargs, sort_keys=True, default=str)
        if key in self._cache:
            self.hits += 1
        else:
            self.misses += 1
            self._cache[key] = self._client.messages.create(**kwargs)
        return self._cache[key]


def ab_compare(fn_a: Callable[[str], str], fn_b: Callable[[str], str], inputs: list[str], score: Callable[[str, str], float]) -> dict:
    """Run both prompt versions on every input and score each output with score(input, output). Return
    {"a": wins for a, "b": wins for b, "tie": ties}."""
    # How you decide whether "prompt v2" really beats "prompt v1": on data, not on one example.
    result = {"a": 0, "b": 0, "tie": 0}
    for x in inputs:
        sa, sb = score(x, fn_a(x)), score(x, fn_b(x))
        result["a" if sa > sb else "b" if sb > sa else "tie"] += 1
    return result


def assert_length(text: str, min_words: int, max_words: int) -> None:
    """Raise AssertionError with a helpful message if `text` has fewer than min_words or more than
    max_words words (split on whitespace)."""
    n = len(text.split())
    assert min_words <= n <= max_words, f"expected {min_words}-{max_words} words, got {n}"
