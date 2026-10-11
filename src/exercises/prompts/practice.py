# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k prompts
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/prompts/practice.py

"""Prompt practice: XML tags, output schemas, classification, chaining, and handling stop reasons."""

import json
import re

MODEL = "claude-opus-5-5"


def _text(response):
    return "".join(b.text for b in response.content if b.type == "text")


def extract_tag(text: str, tag: str) -> list[str]:
    """Return the stripped contents of every <tag>...</tag> in `text`, in order."""
    raise NotImplementedError("Your turn: write this one")


def validate_schema(data, schema: dict, path: str = "$") -> list[str]:
    """Check `data` against a small subset of JSON Schema: "type" (object, array, string, integer,
    number, boolean), "required", "properties", "items" and "enum". Return a list of error strings like
    "$.age: expected integer" or "$: missing name". An empty list means valid."""
    raise NotImplementedError("Your turn: write this one")


def structured_request(question: str, schema: dict) -> dict:
    """Build messages.create() kwargs that ask for JSON matching `schema` with structured outputs:
    model MODEL, max_tokens 1024, one user message, and output_config {"format": {"type":
    "json_schema", "schema": schema}}."""
    raise NotImplementedError("Your turn: write this one")


def classify(client, text: str, labels: list[str]) -> str:
    """Ask Claude to classify `text` into exactly one of `labels`, answering inside <label></label> tags.
    Return the label (matched case-insensitively), or "unknown" if the reply holds no valid label."""
    raise NotImplementedError("Your turn: write this one")


def summarize_then_extract(client, document: str) -> tuple[str, list[str]]:
    """Prompt chaining. Call 1: ask for a one-paragraph summary of `document`. Call 2: send that summary
    and ask for the action items as a JSON array of strings. Return (summary, action_items)."""
    raise NotImplementedError("Your turn: write this one")


def check_stop_reason(response) -> tuple[str, str]:
    """Read response.stop_reason and return (status, text): "ok" for end_turn or stop_sequence,
    "truncated" for max_tokens, "refused" for refusal, "tool_use" for tool_use, otherwise "unknown".
    The text is the joined text blocks."""
    raise NotImplementedError("Your turn: write this one")


def system_prompt_for_tester(product: str, rules: list[str]) -> str:
    """Write a system prompt for a QA assistant: "You are a senior SDET testing {product}.", then
    "Follow these rules:" and each rule as a "- " bullet, then "If you are unsure, say so instead of
    guessing." Join lines with newlines."""
    raise NotImplementedError("Your turn: write this one")
