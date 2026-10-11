"""Prompt practice: XML tags, output schemas, classification, chaining, and handling stop reasons."""

import json
import re

MODEL = "claude-opus-5-5"


def _text(response):
    return "".join(b.text for b in response.content if b.type == "text")


def extract_tag(text: str, tag: str) -> list[str]:
    """Return the stripped contents of every <tag>...</tag> in `text`, in order."""
    # Ask Claude to answer inside <answer> tags and you can find the answer even if it adds prose.
    return [m.strip() for m in re.findall(rf"<{tag}>(.*?)</{tag}>", text, re.S)]


def validate_schema(data, schema: dict, path: str = "$") -> list[str]:
    """Check `data` against a small subset of JSON Schema: "type" (object, array, string, integer,
    number, boolean), "required", "properties", "items" and "enum". Return a list of error strings like
    "$.age: expected integer" or "$: missing name". An empty list means valid."""
    # The SDET's contract test for LLM output: never trust the shape, check it.
    types = {"object": dict, "array": list, "string": str, "boolean": bool,
             "integer": int, "number": (int, float)}
    errors = []
    t = schema.get("type")
    if t:
        ok = isinstance(data, types[t]) and not (t in ("integer", "number") and isinstance(data, bool))
        if not ok:
            return [f"{path}: expected {t}"]
    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{path}: {data!r} not in enum")
    if isinstance(data, dict):
        for key in schema.get("required", []):
            if key not in data:
                errors.append(f"{path}: missing {key}")
        for key, sub in schema.get("properties", {}).items():
            if key in data:
                errors.extend(validate_schema(data[key], sub, f"{path}.{key}"))
    if isinstance(data, list) and "items" in schema:
        for i, item in enumerate(data):
            errors.extend(validate_schema(item, schema["items"], f"{path}[{i}]"))
    return errors


def structured_request(question: str, schema: dict) -> dict:
    """Build messages.create() kwargs that ask for JSON matching `schema` with structured outputs:
    model MODEL, max_tokens 1024, one user message, and output_config {"format": {"type":
    "json_schema", "schema": schema}}."""
    # With structured outputs the API guarantees the reply parses and matches the schema.
    return {
        "model": MODEL,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": question}],
        "output_config": {"format": {"type": "json_schema", "schema": schema}},
    }


def classify(client, text: str, labels: list[str]) -> str:
    """Ask Claude to classify `text` into exactly one of `labels`, answering inside <label></label> tags.
    Return the label (matched case-insensitively), or "unknown" if the reply holds no valid label."""
    prompt = (
        f"Classify the text into exactly one of these labels: {', '.join(labels)}.\n"
        f"<text>{text}</text>\nAnswer with the label inside <label></label> tags."
    )
    reply = _text(client.messages.create(model=MODEL, max_tokens=256,
                                         messages=[{"role": "user", "content": prompt}]))
    found = extract_tag(reply, "label")
    by_lower = {l.lower(): l for l in labels}
    return by_lower.get(found[0].lower(), "unknown") if found else "unknown"


def summarize_then_extract(client, document: str) -> tuple[str, list[str]]:
    """Prompt chaining. Call 1: ask for a one-paragraph summary of `document`. Call 2: send that summary
    and ask for the action items as a JSON array of strings. Return (summary, action_items)."""
    # Two small prompts are easier to test and debug than one big one: you can assert on each step.
    summary = _text(client.messages.create(
        model=MODEL, max_tokens=1024,
        messages=[{"role": "user", "content": f"Summarise in one paragraph:\n<document>{document}</document>"}]))
    items_reply = _text(client.messages.create(
        model=MODEL, max_tokens=1024,
        messages=[{"role": "user", "content":
                   f"List the action items in this summary as a JSON array of strings only.\n<summary>{summary}</summary>"}]))
    start, end = items_reply.find("["), items_reply.rfind("]")
    return summary, json.loads(items_reply[start:end + 1])


def check_stop_reason(response) -> tuple[str, str]:
    """Read response.stop_reason and return (status, text): "ok" for end_turn or stop_sequence,
    "truncated" for max_tokens, "refused" for refusal, "tool_use" for tool_use, otherwise "unknown".
    The text is the joined text blocks."""
    # Always check stop_reason before trusting content. A truncated JSON answer won't parse.
    status = {"end_turn": "ok", "stop_sequence": "ok", "max_tokens": "truncated",
              "refusal": "refused", "tool_use": "tool_use"}.get(response.stop_reason, "unknown")
    return status, _text(response)


def system_prompt_for_tester(product: str, rules: list[str]) -> str:
    """Write a system prompt for a QA assistant: "You are a senior SDET testing {product}.", then
    "Follow these rules:" and each rule as a "- " bullet, then "If you are unsure, say so instead of
    guessing." Join lines with newlines."""
    lines = [f"You are a senior SDET testing {product}.", "Follow these rules:"]
    lines += [f"- {r}" for r in rules]
    lines.append("If you are unsure, say so instead of guessing.")
    return "\n".join(lines)
