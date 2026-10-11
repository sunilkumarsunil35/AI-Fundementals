import pytest

from common.fake_claude import Message, TextBlock, text_reply, tool_call
from common.target import load

P = load("agents", "problems")


def test_make_tool():
    tool = P.make_tool("get_order", "Look up an order by id.", {"order_id": ("string", "The order id")}, ["order_id"])
    assert tool == {
        "name": "get_order", "description": "Look up an order by id.",
        "input_schema": {"type": "object", "properties": {"order_id": {"type": "string", "description": "The order id"}},
                         "required": ["order_id"]},
    }


def test_tool_calls():
    r = tool_call("get_order", {"order_id": "A1"}, text="Checking.")
    (id, name, inp), = P.tool_calls(r)
    assert id.startswith("toolu_") and name == "get_order" and inp == {"order_id": "A1"}
    assert P.tool_calls(text_reply("no tools")) == []


def test_tool_result():
    assert P.tool_result("t1", 42) == {"type": "tool_result", "tool_use_id": "t1", "content": "42"}
    assert P.tool_result("t1", "boom", True)["is_error"] is True


def test_execute_tool_calls():
    a = tool_call("add", {"a": 1, "b": 2})
    b = tool_call("divide", {"a": 1, "b": 0})
    c = tool_call("nope", {})
    response = Message(a.content + b.content + c.content, "tool_use")
    registry = {"add": lambda a, b: a + b, "divide": lambda a, b: a / b}
    results = P.execute_tool_calls(response, registry)
    assert [r["content"] for r in results] == ["3", "division by zero", "unknown tool: nope"]
    assert [r.get("is_error", False) for r in results] == [False, True, True]


def test_agent_loop(fake_claude):
    client = fake_claude([tool_call("get_weather", {"city": "Pune"}), text_reply("It is 31C in Pune.")])
    tools = [P.make_tool("get_weather", "Weather for a city", {"city": ("string", "City")}, ["city"])]
    answer = P.agent_loop(client, "Weather in Pune?", tools, {"get_weather": lambda city: f"{city}: 31C"})
    assert answer == "It is 31C in Pune."
    second = client.calls[1]
    assert second["tools"] == tools
    assert [m["role"] for m in second["messages"]] == ["user", "assistant", "user"]
    assert second["messages"][2]["content"][0]["content"] == "Pune: 31C"


def test_agent_loop_stops(fake_claude):
    client = fake_claude(responder=lambda kw: tool_call("ping", {}))
    with pytest.raises(RuntimeError) as err:
        P.agent_loop(client, "loop forever", [], {"ping": lambda: "pong"}, max_steps=3)
    if isinstance(err.value, NotImplementedError):  # NotImplementedError is a RuntimeError too
        raise err.value
    assert len(client.calls) == 3
