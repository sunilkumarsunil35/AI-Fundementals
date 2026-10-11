# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k llm_testing
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/llm_testing/practice.py

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
    raise NotImplementedError("Your turn: write this one")


def llm_judge(client, question: str, answer: str, rubric: str) -> int:
    """Send judge_prompt(...) to Claude (model MODEL, max_tokens 1024) and return the score in the reply.
    Raise ValueError if the reply holds no <score> tag with 1-5."""
    raise NotImplementedError("Your turn: write this one")


def regressions(baseline: dict[str, str], current: dict[str, str], similarity: Callable[[str, str], float], threshold: float) -> list[str]:
    """Compare today's answers with the approved baseline answers, id by id. Return the sorted ids that
    are missing from `current` or whose similarity to the baseline is below `threshold`."""
    raise NotImplementedError("Your turn: write this one")


def latency_stats(durations_ms: list[float]) -> dict:
    """Return {"p50": .., "p95": .., "max": ..} using the nearest-rank percentile: sort the values and
    take the one at position ceil(p/100 * n) (1-based)."""
    raise NotImplementedError("Your turn: write this one")


def run_cost(usages: list[dict], input_per_mtok: float, output_per_mtok: float) -> float:
    """Each usage dict has "input_tokens" and "output_tokens". Prices are dollars per million tokens.
    Return the total cost in dollars, rounded to 6 decimal places."""
    raise NotImplementedError("Your turn: write this one")


class CachingClient:
    """Wrap a client so identical messages.create() requests are answered from a cache. Tests that rerun
    the same prompt cost nothing after the first call."""

    def __init__(self, client):
        """Keep `client`, start an empty cache, and expose `self.messages` with a create() method and
        `self.hits` / `self.misses` counters."""
        raise NotImplementedError("Your turn: write this one")

    def create(self, **kwargs):
        """Return the cached response for these exact kwargs, or call the real client and cache it."""
        raise NotImplementedError("Your turn: write this one")


def ab_compare(fn_a: Callable[[str], str], fn_b: Callable[[str], str], inputs: list[str], score: Callable[[str, str], float]) -> dict:
    """Run both prompt versions on every input and score each output with score(input, output). Return
    {"a": wins for a, "b": wins for b, "tie": ties}."""
    raise NotImplementedError("Your turn: write this one")


def assert_length(text: str, min_words: int, max_words: int) -> None:
    """Raise AssertionError with a helpful message if `text` has fewer than min_words or more than
    max_words words (split on whitespace)."""
    raise NotImplementedError("Your turn: write this one")
