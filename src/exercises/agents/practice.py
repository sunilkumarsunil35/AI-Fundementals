# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k agents
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/agents/practice.py

"""Agent practice: validating tool input, a safe calculator tool, approval policies and auto-built schemas."""

import ast
import inspect
import operator
import re
from typing import Callable


def validate_tool_input(schema: dict, inputs: dict) -> list[str]:
    """Check tool `inputs` against an input_schema: every required key is present ("missing X"), there
    are no keys outside properties ("unexpected X"), and values match the property "type" (string,
    integer, number, boolean, array, object; "X: expected T"). Return the errors, missing first, then
    unexpected, then type errors in key order."""
    raise NotImplementedError("Your turn: write this one")


_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos}


def safe_calculate(expression: str) -> float:
    """Evaluate an arithmetic expression with numbers, + - * / ** and parentheses, without eval(). Raise
    ValueError for anything else (names, calls, attributes...)."""
    raise NotImplementedError("Your turn: write this one")


def tools_used(messages: list[dict]) -> list[str]:
    """Go through a conversation's messages and return the name of every tool_use block in assistant
    messages, in order. Content blocks may be dicts or objects with .type and .name."""
    raise NotImplementedError("Your turn: write this one")


def apply_policy(calls: list[tuple[str, str, dict]], policy: dict[str, str], approve: Callable[[str, dict], bool]) -> tuple[list[str], list[str]]:
    """Each call is (id, name, input). policy maps tool name to "allow", "deny" or "ask"; tools not in
    the policy are "ask". For "ask", call approve(name, input). Return (allowed ids, blocked ids)."""
    raise NotImplementedError("Your turn: write this one")


def parse_plan(text: str) -> list[str]:
    """Return the steps of a numbered plan ("1. Do this" or "2) Do that", one per line), stripped, in
    order. Ignore other lines."""
    raise NotImplementedError("Your turn: write this one")


def tool_from_function(fn: Callable) -> dict:
    """Build a Claude tool definition from a Python function: name = function name, description = its
    docstring (cleaned with inspect.getdoc), and one property per parameter typed from its annotation
    (str string, int integer, float number, bool boolean, list array, dict object). Parameters without a
    default are required."""
    raise NotImplementedError("Your turn: write this one")


def budgeted_steps(usages: list[dict], budget_tokens: int) -> int:
    """An agent reports usage after each step ({"input_tokens", "output_tokens"}). Return how many steps
    fit before the running total of all tokens would exceed `budget_tokens`."""
    raise NotImplementedError("Your turn: write this one")
