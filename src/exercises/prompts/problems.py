# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k prompts
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/prompts/problems.py

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
    raise NotImplementedError("Your turn: write this one")


def build_request(system: str, history: list[tuple[str, str]], user_input: str, max_tokens: int = 1024) -> dict:
    """Build the keyword arguments for client.messages.create(): model MODEL, max_tokens, the `system`
    prompt, and messages made of the (user, assistant) turns in `history` followed by `user_input`."""
    raise NotImplementedError("Your turn: write this one")


def few_shot_prompt(instruction: str, examples: list[tuple[str, str]], query: str) -> str:
    """Build a few-shot prompt: the instruction, then each example as
    <example><input>..</input><output>..</output></example> on its own line, then <input>query</input>.
    Join the parts with newlines."""
    raise NotImplementedError("Your turn: write this one")


def response_text(response) -> str:
    """Return the text of a Messages API response: join the .text of every block whose type is "text".
    Skip other blocks (thinking, tool_use)."""
    raise NotImplementedError("Your turn: write this one")


def ask_claude(client, question: str) -> str:
    """Send `question` as one user message (model MODEL, max_tokens 1024) and return the reply text."""
    raise NotImplementedError("Your turn: write this one")


def extract_json(text: str):
    """Pull the JSON out of a model reply. If there is a ```json ... ``` (or plain ```) fenced block, parse
    its contents. Otherwise parse from the first "{" or "[" to the matching last "}" or "]". Raise
    ValueError if there is no JSON."""
    raise NotImplementedError("Your turn: write this one")
