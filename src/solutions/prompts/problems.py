"""Prompt engineering with Claude: building requests in code and reading the answers back reliably.

Every function that talks to a model takes a `client`. In tests that is FakeClaude; in
scripts/try_with_claude.py it is the real `anthropic.Anthropic()`. Same code, both ways.
"""

import json
import re
import string

MODEL = "claude-opus-5-5"


def fill_template(template: str, values: dict) -> str:
    """Fill the {name} placeholders in `template` from `values`. If any placeholder has no value, raise
    KeyError naming every missing one (sorted, comma-separated)."""
    # A prompt template is test data: it should fail loudly when a field is missing, not send "{name}".
    fields = {f for _, f, _, _ in string.Formatter().parse(template) if f}
    missing = sorted(fields - values.keys())
    if missing:
        raise KeyError(", ".join(missing))
    return template.format(**values)


def build_request(system: str, history: list[tuple[str, str]], user_input: str, max_tokens: int = 1024) -> dict:
    """Build the keyword arguments for client.messages.create(): model MODEL, max_tokens, the `system`
    prompt, and messages made of the (user, assistant) turns in `history` followed by `user_input`."""
    # The Messages API is stateless: you resend the whole conversation every time.
    messages = []
    for user, assistant in history:
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": assistant})
    messages.append({"role": "user", "content": user_input})
    return {"model": MODEL, "max_tokens": max_tokens, "system": system, "messages": messages}


def few_shot_prompt(instruction: str, examples: list[tuple[str, str]], query: str) -> str:
    """Build a few-shot prompt: the instruction, then each example as
    <example><input>..</input><output>..</output></example> on its own line, then <input>query</input>.
    Join the parts with newlines."""
    # Claude follows XML tags well: they separate instructions from data and make the pattern obvious.
    lines = [instruction]
    for inp, out in examples:
        lines.append(f"<example><input>{inp}</input><output>{out}</output></example>")
    lines.append(f"<input>{query}</input>")
    return "\n".join(lines)


def response_text(response) -> str:
    """Return the text of a Messages API response: join the .text of every block whose type is "text".
    Skip other blocks (thinking, tool_use)."""
    # response.content[0].text breaks as soon as the first block is a thinking or tool_use block.
    return "".join(b.text for b in response.content if b.type == "text")


def ask_claude(client, question: str) -> str:
    """Send `question` as one user message (model MODEL, max_tokens 1024) and return the reply text."""
    response = client.messages.create(
        model=MODEL, max_tokens=1024, messages=[{"role": "user", "content": question}]
    )
    return response_text(response)


def extract_json(text: str):
    """Pull the JSON out of a model reply. If there is a ```json ... ``` (or plain ```) fenced block, parse
    its contents. Otherwise parse from the first "{" or "[" to the matching last "}" or "]". Raise
    ValueError if there is no JSON."""
    # Models wrap JSON in prose and code fences. Prefer structured outputs when you can; parse safely
    # when you can't.
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence:
        return json.loads(fence.group(1))
    starts = [i for i in (text.find("{"), text.find("[")) if i != -1]
    if not starts:
        raise ValueError("no JSON found")
    start = min(starts)
    end = text.rfind("}" if text[start] == "{" else "]")
    if end < start:
        raise ValueError("no JSON found")
    return json.loads(text[start:end + 1])
