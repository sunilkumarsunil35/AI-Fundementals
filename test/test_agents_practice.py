import pytest

from common.fake_claude import tool_call
from common.target import load

P = load("agents", "practice")

SCHEMA = {"type": "object", "required": ["city", "days"],
          "properties": {"city": {"type": "string"}, "days": {"type": "integer"}, "metric": {"type": "boolean"}}}


def test_validate_tool_input():
    assert P.validate_tool_input(SCHEMA, {"city": "Pune", "days": 3}) == []
    assert P.validate_tool_input(SCHEMA, {"days": "3", "metric": 1, "x": 0}) == [
        "missing city", "unexpected x", "days: expected integer", "metric: expected boolean"]


def test_safe_calculate():
    assert P.safe_calculate("2 * (3 + 4) ** 2 / 7") == 14
    assert P.safe_calculate("-3 + 1.5") == -1.5
    for bad in ["__import__('os')", "x + 1", "open('f')", "2 +"]:
        with pytest.raises(ValueError):
            P.safe_calculate(bad)


def test_tools_used():
    msgs = [
        {"role": "user", "content": "refund order A1"},
        {"role": "assistant", "content": tool_call("get_order", {"id": "A1"}).content},
        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "x", "content": "ok"}]},
        {"role": "assistant", "content": [{"type": "text", "text": "ok"}, {"type": "tool_use", "id": "y", "name": "refund", "input": {}}]},
    ]
    assert P.tools_used(msgs) == ["get_order", "refund"]


def test_apply_policy():
    calls = [("1", "search", {}), ("2", "delete_user", {"id": 7}), ("3", "send_email", {"to": "a"}), ("4", "pay", {})]
    asked = []
    approve = lambda name, inp: asked.append(name) or name == "send_email"
    allowed, blocked = P.apply_policy(calls, {"search": "allow", "delete_user": "deny"}, approve)
    assert allowed == ["1", "3"] and blocked == ["2", "4"] and asked == ["send_email", "pay"]


def test_parse_plan():
    text = "Plan:\n1. Open login page\n2) Enter bad password\n  3. Check the error \nDone."
    assert P.parse_plan(text) == ["Open login page", "Enter bad password", "Check the error"]


def test_tool_from_function():
    def search_tests(query: str, limit: int = 10, flaky_only: bool = False):
        """Search the test suite by name."""
    assert P.tool_from_function(search_tests) == {
        "name": "search_tests", "description": "Search the test suite by name.",
        "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer"},
                                                          "flaky_only": {"type": "boolean"}}, "required": ["query"]},
    }


def test_budgeted_steps():
    usages = [{"input_tokens": 100, "output_tokens": 50}] * 4
    assert P.budgeted_steps(usages, 300) == 2
    assert P.budgeted_steps(usages, 10_000) == 4
