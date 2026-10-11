import pytest

from common.fake_claude import text_reply, tool_call
from common.target import load

P = load("prompts", "problems")


def test_fill_template():
    assert P.fill_template("Test {feature} on {browser}", {"feature": "login", "browser": "Chrome"}) == "Test login on Chrome"
    with pytest.raises(KeyError, match="browser, feature"):
        P.fill_template("Test {feature} on {browser}", {})


def test_build_request():
    req = P.build_request("You are a tester.", [("hi", "hello")], "write a test")
    assert req == {
        "model": "claude-opus-5-5", "max_tokens": 1024, "system": "You are a tester.",
        "messages": [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"},
                     {"role": "user", "content": "write a test"}],
    }


def test_few_shot_prompt():
    prompt = P.few_shot_prompt("Classify the bug severity.", [("app crashes", "high"), ("typo", "low")], "slow page")
    assert prompt.splitlines() == [
        "Classify the bug severity.",
        "<example><input>app crashes</input><output>high</output></example>",
        "<example><input>typo</input><output>low</output></example>",
        "<input>slow page</input>",
    ]


def test_response_text():
    assert P.response_text(text_reply("Paris")) == "Paris", "skip the thinking block"
    assert P.response_text(tool_call("search", {"q": "x"}, text="Let me look.")) == "Let me look."


def test_ask_claude(fake_claude):
    client = fake_claude(["Paris"])
    assert P.ask_claude(client, "Capital of France?") == "Paris"
    call = client.calls[0]
    assert call["model"] == "claude-opus-5-5" and call["max_tokens"] == 1024
    assert call["messages"] == [{"role": "user", "content": "Capital of France?"}]


def test_extract_json():
    assert P.extract_json('Sure! ```json\n{"ok": true}\n``` Hope that helps') == {"ok": True}
    assert P.extract_json('Here: {"a": [1, 2]} done') == {"a": [1, 2]}
    assert P.extract_json('Cases: ["a", "b"]') == ["a", "b"]
    with pytest.raises(ValueError):
        P.extract_json("no json here")
