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
    # Redact before you log prompts or send customer data to any third-party API.
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[EMAIL]", text)
    text = re.sub(r"\b\d(?:[ -]?\d){12,15}\b", "[CARD]", text)
    text = re.sub(r"\+?\b\d(?:[ -]?\d){9,11}\b", "[PHONE]", text)
    return text


def looks_like_injection(text: str) -> bool:
    """Return True if `text` matches any regex in INJECTION_PATTERNS (case-insensitive)."""
    # A first line of defence only. Real defence is architecture: least-privilege tools, untrusted data
    # kept in tags, and human approval for risky actions.
    return any(re.search(p, text, re.I) for p in INJECTION_PATTERNS)


def estimate_cost(input_tokens: int, output_tokens: int, model: str, prices: dict[str, tuple[float, float]]) -> float:
    """`prices` maps a model id to (input $ per million tokens, output $ per million tokens). Return the
    cost in dollars rounded to 6 places. Raise KeyError for an unknown model."""
    inp, out = prices[model]
    return round((input_tokens * inp + output_tokens * out) / 1_000_000, 6)


class TokenBucket:
    """A rate limiter: holds up to `capacity` tokens and refills `rate` tokens per second."""

    def __init__(self, capacity: float, rate: float, clock: Callable[[], float]):
        """Start full. `clock` returns the current time in seconds (injected so tests can fake time)."""
        self.capacity = capacity
        self.rate = rate
        self.clock = clock
        self.tokens = capacity
        self.updated = clock()

    def allow(self, cost: float = 1) -> bool:
        """Refill for the time passed since the last call (never above capacity). If at least `cost`
        tokens are available, take them and return True; otherwise return False."""
        # Client-side throttling keeps a big test run under the API's rate limits instead of hitting 429s.
        now = self.clock()
        self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.rate)
        self.updated = now
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False
