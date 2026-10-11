"""Guardrail practice: card checks, secret masking, moderation, red-teaming and a guarded Claude call."""

import re
from typing import Callable

MODEL = "claude-opus-5-5"


def luhn_valid(number: str) -> bool:
    """Return True if the digits in `number` (ignore spaces and dashes) pass the Luhn checksum: from the
    right, double every second digit, subtract 9 from results over 9, and the total must divide by 10.
    Fewer than 2 digits is False."""
    # Cuts false positives in card redaction: a random 16-digit order id usually fails Luhn.
    digits = [int(c) for c in number if c.isdigit()]
    if len(digits) < 2:
        return False
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def mask_secrets(text: str) -> str:
    """Replace secrets with [SECRET]: Anthropic-style keys (sk-ant- followed by letters, digits, - or _),
    AWS access key ids (AKIA + 16 upper-case letters or digits), and bearer tokens ("Bearer " + the
    token: keep the word Bearer)."""
    # Test logs and LLM transcripts leak credentials more often than code does.
    text = re.sub(r"sk-ant-[\w-]+", "[SECRET]", text)
    text = re.sub(r"\bAKIA[A-Z0-9]{16}\b", "[SECRET]", text)
    text = re.sub(r"(Bearer )[\w.\-~+/]+=*", r"\1[SECRET]", text)
    return text


def moderate(text: str, blocklist: list[str]) -> tuple[bool, list[str]]:
    """Return (ok, hits): hits are the blocklist words found in `text` as whole words, case-insensitive,
    in blocklist order. ok is True when there are no hits."""
    hits = [w for w in blocklist if re.search(rf"\b{re.escape(w)}\b", text, re.I)]
    return not hits, hits


def red_team(fn: Callable[[str], str], attacks: list[str], forbidden: list[str]) -> list[str]:
    """Send each attack prompt through `fn`. Return the attacks whose reply contains any forbidden string
    (case-insensitive): those are the leaks."""
    # Plant a canary (like a fake secret in the system prompt) and check the attacks can't pull it out.
    leaks = []
    for attack in attacks:
        reply = fn(attack).lower()
        if any(f.lower() in reply for f in forbidden):
            leaks.append(attack)
    return leaks


def trim_history(messages: list[dict], max_tokens: int) -> list[dict]:
    """Keep the conversation under budget by dropping the oldest messages (always keep the last one).
    Count each message as ceil(len(content) / 4) tokens. Return the shortest suffix-trimmed list whose
    total fits, or just the last message."""
    def cost(m):
        return -(-len(m["content"]) // 4)
    kept = list(messages)
    while len(kept) > 1 and sum(cost(m) for m in kept) > max_tokens:
        kept.pop(0)
    return kept


def guarded_ask(client, user_input: str, system: str, blocklist: list[str]) -> dict:
    """Wrap one Claude call in guardrails. If user_input looks like a prompt injection (it contains
    "ignore previous instructions" or "reveal your system prompt", case-insensitive), return
    {"status": "blocked_input", "text": ""} without calling Claude. Otherwise redact emails in the input
    to [EMAIL], call Claude (model MODEL, max_tokens 1024, `system`), and if the reply contains a
    blocklist word (whole word, case-insensitive) return {"status": "blocked_output", "text": ""}; else
    {"status": "ok", "text": reply}."""
    low = user_input.lower()
    if "ignore previous instructions" in low or "reveal your system prompt" in low:
        return {"status": "blocked_input", "text": ""}
    clean = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[EMAIL]", user_input)
    response = client.messages.create(model=MODEL, max_tokens=1024, system=system,
                                      messages=[{"role": "user", "content": clean}])
    reply = "".join(b.text for b in response.content if b.type == "text")
    if any(re.search(rf"\b{re.escape(w)}\b", reply, re.I) for w in blocklist):
        return {"status": "blocked_output", "text": ""}
    return {"status": "ok", "text": reply}
