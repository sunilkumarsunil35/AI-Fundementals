"""A stand-in for `anthropic.Anthropic()` so every test runs offline, for free, and gives the same
answer every time.

It has the same shape as the real client: `client.messages.create(**kwargs)` returns a message with
`.content` (a list of blocks), `.stop_reason` and `.usage`. So code written against FakeClaude also
runs against the real Claude API unchanged. That is the main SDET lesson here: put the model behind
an interface you can replace in tests.

    client = FakeClaude(["Paris"])                       # scripted replies, in order
    client = FakeClaude(responder=lambda kw: "echo")     # or compute a reply from the request
    client.messages.create(model="claude-opus-5-5", max_tokens=100,
                           messages=[{"role": "user", "content": "Capital of France?"}])
    client.calls                                         # every request you sent, as kwargs dicts
"""

from dataclasses import dataclass, field
from itertools import count

_ids = count(1)


@dataclass
class TextBlock:
    text: str
    type: str = "text"


@dataclass
class ThinkingBlock:
    """Real responses can start with a thinking block. Code that reads `content[0].text` breaks."""

    thinking: str = ""
    type: str = "thinking"


@dataclass
class ToolUseBlock:
    name: str
    input: dict
    id: str = field(default_factory=lambda: f"toolu_{next(_ids):04d}")
    type: str = "tool_use"


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class Message:
    content: list
    stop_reason: str = "end_turn"
    usage: Usage = field(default_factory=Usage)
    model: str = "claude-opus-5-5"
    role: str = "assistant"
    stop_details: object = None


class APIError(Exception):
    """Like the SDK's APIStatusError: it carries the HTTP status code (429 rate limit, 529 overloaded...)."""

    def __init__(self, status_code, message="API error"):
        super().__init__(f"{status_code}: {message}")
        self.status_code = status_code


def text_reply(text, stop_reason="end_turn", thinking=True):
    """A plain answer. By default it starts with an empty thinking block, like Claude Opus 5.5 does."""
    blocks = ([ThinkingBlock()] if thinking else []) + [TextBlock(text)]
    return Message(blocks, stop_reason, Usage(input_tokens=10, output_tokens=max(1, len(text) // 4)))


def tool_call(name, input, text=None):
    """A reply where Claude asks you to run tool `name` with `input`."""
    blocks = ([TextBlock(text)] if text else []) + [ToolUseBlock(name, input)]
    return Message(blocks, "tool_use", Usage(10, 20))


def _as_message(reply):
    if isinstance(reply, Message):
        return reply
    if isinstance(reply, str):
        return text_reply(reply)
    raise TypeError(f"FakeClaude reply must be str or Message, got {type(reply).__name__}")


class _Messages:
    def __init__(self, owner):
        self._owner = owner

    def create(self, **kwargs):
        owner = self._owner
        if "model" not in kwargs or "max_tokens" not in kwargs or "messages" not in kwargs:
            raise TypeError("messages.create() needs model, max_tokens and messages, like the real API")
        owner.calls.append(kwargs)
        if owner.responder is not None:
            reply = owner.responder(kwargs)
        elif owner.replies:
            reply = owner.replies.pop(0)
        else:
            raise AssertionError("FakeClaude ran out of scripted replies")
        if isinstance(reply, Exception):
            raise reply
        return _as_message(reply)


class FakeClaude:
    def __init__(self, replies=None, responder=None):
        self.replies = list(replies or [])
        self.responder = responder
        self.calls = []
        self.messages = _Messages(self)

    def last_prompt(self):
        """The text of the last user message you sent: handy in tests."""
        content = self.calls[-1]["messages"][-1]["content"]
        if isinstance(content, str):
            return content
        return "".join(b.get("text", "") for b in content if isinstance(b, dict))
