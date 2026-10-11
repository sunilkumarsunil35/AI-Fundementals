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
    types = {"string": str, "integer": int, "number": (int, float), "boolean": bool, "array": list, "object": dict}
    props = schema.get("properties", {})
    errors = [f"missing {k}" for k in schema.get("required", []) if k not in inputs]
    errors += [f"unexpected {k}" for k in inputs if k not in props]
    for k in sorted(inputs):
        if k in props and "type" in props[k]:
            t = props[k]["type"]
            v = inputs[k]
            if not isinstance(v, types[t]) or (t in ("integer", "number") and isinstance(v, bool)):
                errors.append(f"{k}: expected {t}")
    return errors


_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos}


def safe_calculate(expression: str) -> float:
    """Evaluate an arithmetic expression with numbers, + - * / ** and parentheses, without eval(). Raise
    ValueError for anything else (names, calls, attributes...)."""
    # Tools run with your permissions. Never eval() text that came from a model.
    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](walk(node.left), walk(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](walk(node.operand))
        raise ValueError(f"not allowed: {type(node).__name__}")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as e:
        raise ValueError("bad expression") from e
    return walk(tree)


def tools_used(messages: list[dict]) -> list[str]:
    """Go through a conversation's messages and return the name of every tool_use block in assistant
    messages, in order. Content blocks may be dicts or objects with .type and .name."""
    # Asserting on the tool trajectory ("it looked up the order before refunding") is a key agent test.
    names = []
    for m in messages:
        if m["role"] != "assistant" or isinstance(m["content"], str):
            continue
        for b in m["content"]:
            kind = b["type"] if isinstance(b, dict) else b.type
            if kind == "tool_use":
                names.append(b["name"] if isinstance(b, dict) else b.name)
    return names


def apply_policy(calls: list[tuple[str, str, dict]], policy: dict[str, str], approve: Callable[[str, dict], bool]) -> tuple[list[str], list[str]]:
    """Each call is (id, name, input). policy maps tool name to "allow", "deny" or "ask"; tools not in
    the policy are "ask". For "ask", call approve(name, input). Return (allowed ids, blocked ids)."""
    # Human-in-the-loop: reading data can be automatic, deleting or paying should need a yes.
    allowed, blocked = [], []
    for id, name, inp in calls:
        rule = policy.get(name, "ask")
        ok = rule == "allow" or (rule == "ask" and approve(name, inp))
        (allowed if ok else blocked).append(id)
    return allowed, blocked


def parse_plan(text: str) -> list[str]:
    """Return the steps of a numbered plan ("1. Do this" or "2) Do that", one per line), stripped, in
    order. Ignore other lines."""
    return [m.group(1).strip() for m in re.finditer(r"^\s*\d+[.)]\s+(.+)$", text, re.M)]


def tool_from_function(fn: Callable) -> dict:
    """Build a Claude tool definition from a Python function: name = function name, description = its
    docstring (cleaned with inspect.getdoc), and one property per parameter typed from its annotation
    (str string, int integer, float number, bool boolean, list array, dict object). Parameters without a
    default are required."""
    # The idea behind the SDK's @beta_tool decorator: your function signature is the schema.
    types = {str: "string", int: "integer", float: "number", bool: "boolean", list: "array", dict: "object"}
    sig = inspect.signature(fn)
    props, required = {}, []
    for name, p in sig.parameters.items():
        props[name] = {"type": types[p.annotation]}
        if p.default is inspect.Parameter.empty:
            required.append(name)
    return {"name": fn.__name__, "description": inspect.getdoc(fn) or "",
            "input_schema": {"type": "object", "properties": props, "required": required}}


def budgeted_steps(usages: list[dict], budget_tokens: int) -> int:
    """An agent reports usage after each step ({"input_tokens", "output_tokens"}). Return how many steps
    fit before the running total of all tokens would exceed `budget_tokens`."""
    total = 0
    for i, u in enumerate(usages):
        total += u["input_tokens"] + u["output_tokens"]
        if total > budget_tokens:
            return i
    return len(usages)
