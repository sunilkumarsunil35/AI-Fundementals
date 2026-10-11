from common.fake_claude import Message, TextBlock, text_reply
from common.target import load

P = load("prompts", "practice")

SCHEMA = {
    "type": "object", "required": ["name", "priority"],
    "properties": {
        "name": {"type": "string"},
        "priority": {"type": "string", "enum": ["low", "high"]},
        "steps": {"type": "array", "items": {"type": "string"}},
        "estimate": {"type": "integer"},
    },
}


def test_extract_tag():
    assert P.extract_tag("x <answer> 42 </answer> y <answer>7</answer>", "answer") == ["42", "7"]
    assert P.extract_tag("nothing", "answer") == []


def test_validate_schema():
    assert P.validate_schema({"name": "t", "priority": "high", "steps": ["a"], "estimate": 3}, SCHEMA) == []
    errors = P.validate_schema({"priority": "urgent", "steps": ["a", 2], "estimate": True}, SCHEMA)
    assert errors == ["$: missing name", "$.priority: 'urgent' not in enum", "$.steps[1]: expected string",
                      "$.estimate: expected integer"]
    assert P.validate_schema([], SCHEMA) == ["$: expected object"]


def test_structured_request():
    req = P.structured_request("Make a test case", SCHEMA)
    assert req["output_config"] == {"format": {"type": "json_schema", "schema": SCHEMA}}
    assert req["model"] == "claude-opus-5-5" and req["messages"][0]["content"] == "Make a test case"


def test_classify(fake_claude):
    client = fake_claude(["It is <label>Bug</label>.", "<label>praise</label>", "Not sure."])
    assert P.classify(client, "Login crashes", ["bug", "feature"]) == "bug"
    assert "<text>Login crashes</text>" in client.last_prompt()
    assert P.classify(client, "Great app", ["bug", "feature"]) == "unknown"
    assert P.classify(client, "???", ["bug", "feature"]) == "unknown"


def test_summarize_then_extract(fake_claude):
    client = fake_claude(["The team agreed to fix login and add tests.", 'Sure: ["Fix login", "Add tests"]'])
    summary, items = P.summarize_then_extract(client, "long meeting notes")
    assert summary.startswith("The team") and items == ["Fix login", "Add tests"]
    assert len(client.calls) == 2 and "The team agreed" in client.last_prompt()


def test_check_stop_reason():
    assert P.check_stop_reason(text_reply("done")) == ("ok", "done")
    assert P.check_stop_reason(text_reply('{"a": ', stop_reason="max_tokens")) == ("truncated", '{"a": ')
    assert P.check_stop_reason(Message([], "refusal")) == ("refused", "")
    assert P.check_stop_reason(Message([TextBlock("x")], "weird")) == ("unknown", "x")


def test_system_prompt_for_tester():
    assert P.system_prompt_for_tester("Shop", ["Use pytest", "Cite the requirement"]) == (
        "You are a senior SDET testing Shop.\nFollow these rules:\n- Use pytest\n- Cite the requirement\n"
        "If you are unsure, say so instead of guessing.")
