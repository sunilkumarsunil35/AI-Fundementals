# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k guardrails
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/guardrails/problems.py

"""Safety, guardrails and cost: the checks that sit around every production LLM call.

Input guards (PII, prompt injection), output guards (moderation, leaks) and budget guards (cost, rate
limits). They are plain code, so they are the easiest part of an AI feature to unit-test.
"""

import re
from typing import Callable

INJECTION_PATTERNS = [
    r"ignore (all |any )?(the )?(previous|prior|above) (instructions|rules)",
    r"disregard (the )?(system|previous) prompt",
    r"you are now",
    r"reveal (your|the) (system prompt|instructions)",
    r"pretend (to be|you are)",
]


def redact_pii(text: str) -> str:
    """Replace emails with [EMAIL], card numbers (13-16 digits, optionally split by spaces or dashes)
    with [CARD], and phone numbers (an optional +, then 10-12 digits, optionally split by spaces or
    dashes) with [PHONE]. Do cards before phones."""
    raise NotImplementedError("Your turn: write this one")


def looks_like_injection(text: str) -> bool:
    """Return True if `text` matches any regex in INJECTION_PATTERNS (case-insensitive)."""
    raise NotImplementedError("Your turn: write this one")


def estimate_cost(input_tokens: int, output_tokens: int, model: str, prices: dict[str, tuple[float, float]]) -> float:
    """`prices` maps a model id to (input $ per million tokens, output $ per million tokens). Return the
    cost in dollars rounded to 6 places. Raise KeyError for an unknown model."""
    raise NotImplementedError("Your turn: write this one")


class TokenBucket:
    """A rate limiter: holds up to `capacity` tokens and refills `rate` tokens per second."""

    def __init__(self, capacity: float, rate: float, clock: Callable[[], float]):
        """Start full. `clock` returns the current time in seconds (injected so tests can fake time)."""
        raise NotImplementedError("Your turn: write this one")

    def allow(self, cost: float = 1) -> bool:
        """Refill for the time passed since the last call (never above capacity). If at least `cost`
        tokens are available, take them and return True; otherwise return False."""
        raise NotImplementedError("Your turn: write this one")
