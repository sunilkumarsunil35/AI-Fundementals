# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k llm_testing
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/llm_testing/problems.py

"""Testing LLM apps: the heart of the AI SDET job.

LLM output is non-deterministic and free text, so `assert reply == expected` fails. Instead you check
properties (keywords, schema, length), run golden data sets, measure consistency, retry transient
errors and let a second model grade the first.
"""

import re
from collections import Counter
from typing import Callable

RETRYABLE = {408, 409, 429, 500, 502, 503, 504, 529}


def missing_keywords(text: str, keywords: list[str]) -> list[str]:
    """Return the keywords that do not appear in `text` (case-insensitive), in their original order."""
    raise NotImplementedError("Your turn: write this one")


def run_golden_set(fn: Callable[[str], str], cases: list[dict]) -> dict:
    """Run `fn` on each case's "input" and check that the output contains every keyword in the case's
    "expected" list (case-insensitive). Return {"passed": n, "failed": n, "failures": [ids of failed
    cases]}. A case whose fn call raises counts as failed."""
    raise NotImplementedError("Your turn: write this one")


def consistency_rate(fn: Callable[[str], str], prompt: str, runs: int) -> float:
    """Call fn(prompt) `runs` times. Compare answers after stripping and lower-casing. Return the
    fraction of runs that gave the most common answer."""
    raise NotImplementedError("Your turn: write this one")


def call_with_retry(fn: Callable[[], object], retries: int, base_delay: float, sleep: Callable[[float], None]):
    """Call fn(). If it raises an exception whose `status_code` is in RETRYABLE, sleep base_delay * 2**n
    (n = 0, 1, 2...) and try again, up to `retries` retries. Re-raise anything else at once, and the last
    error when retries run out."""
    raise NotImplementedError("Your turn: write this one")


def parse_judge_score(text: str) -> int:
    """Read a 1-5 score from a judge model's reply. Accept "<score>4</score>" or "Score: 4" (any case).
    Raise ValueError if there is no score or it is outside 1-5."""
    raise NotImplementedError("Your turn: write this one")
