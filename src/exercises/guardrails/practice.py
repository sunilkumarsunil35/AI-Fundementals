# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k guardrails
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/guardrails/practice.py

"""Guardrail practice: card checks, secret masking, moderation, red-teaming and a guarded Claude call."""

import re
from typing import Callable

MODEL = "claude-opus-5-5"


def luhn_valid(number: str) -> bool:
    """Return True if the digits in `number` (ignore spaces and dashes) pass the Luhn checksum: from the
    right, double every second digit, subtract 9 from results over 9, and the total must divide by 10.
    Fewer than 2 digits is False."""
    raise NotImplementedError("Your turn: write this one")


def mask_secrets(text: str) -> str:
    """Replace secrets with [SECRET]: Anthropic-style keys (sk-ant- followed by letters, digits, - or _),
    AWS access key ids (AKIA + 16 upper-case letters or digits), and bearer tokens ("Bearer " + the
    token: keep the word Bearer)."""
    raise NotImplementedError("Your turn: write this one")


def moderate(text: str, blocklist: list[str]) -> tuple[bool, list[str]]:
    """Return (ok, hits): hits are the blocklist words found in `text` as whole words, case-insensitive,
    in blocklist order. ok is True when there are no hits."""
    raise NotImplementedError("Your turn: write this one")


def red_team(fn: Callable[[str], str], attacks: list[str], forbidden: list[str]) -> list[str]:
    """Send each attack prompt through `fn`. Return the attacks whose reply contains any forbidden string
    (case-insensitive): those are the leaks."""
    raise NotImplementedError("Your turn: write this one")


def trim_history(messages: list[dict], max_tokens: int) -> list[dict]:
    """Keep the conversation under budget by dropping the oldest messages (always keep the last one).
    Count each message as ceil(len(content) / 4) tokens. Return the shortest suffix-trimmed list whose
    total fits, or just the last message."""
    raise NotImplementedError("Your turn: write this one")


def guarded_ask(client, user_input: str, system: str, blocklist: list[str]) -> dict:
    """Wrap one Claude call in guardrails. If user_input looks like a prompt injection (it contains
    "ignore previous instructions" or "reveal your system prompt", case-insensitive), return
    {"status": "blocked_input", "text": ""} without calling Claude. Otherwise redact emails in the input
    to [EMAIL], call Claude (model MODEL, max_tokens 1024, `system`), and if the reply contains a
    blocklist word (whole word, case-insensitive) return {"status": "blocked_output", "text": ""}; else
    {"status": "ok", "text": reply}."""
    raise NotImplementedError("Your turn: write this one")
