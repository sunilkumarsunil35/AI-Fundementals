# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k agents
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/agents/problems.py

"""Tool use and agents: let Claude call your functions, and keep the loop safe and testable.

Claude never runs your code. It replies with a tool_use block naming a tool and its input; you run
it and send back a tool_result. An agent is that exchange in a loop, until Claude stops asking.
"""

MODEL = "claude-opus-5-5"


def make_tool(name: str, description: str, params: dict[str, tuple[str, str]], required: list[str]) -> dict:
    """Build a Claude tool definition: {"name", "description", "input_schema"} where input_schema is
    {"type": "object", "properties": {param: {"type": type, "description": desc}}, "required": required}.
    `params` maps each parameter name to (json type, description)."""
    raise NotImplementedError("Your turn: write this one")


def tool_calls(response) -> list[tuple[str, str, dict]]:
    """Return (id, name, input) for every block of type "tool_use" in response.content, in order."""
    raise NotImplementedError("Your turn: write this one")


def tool_result(tool_use_id: str, output, is_error: bool = False) -> dict:
    """Build a tool_result block: {"type": "tool_result", "tool_use_id": ..., "content": str(output)},
    plus "is_error": True when is_error is set."""
    raise NotImplementedError("Your turn: write this one")


def execute_tool_calls(response, registry: dict) -> list[dict]:
    """Run every tool call in `response` with registry[name](**input) and return one tool_result per
    call, in order. An unknown tool gives an error result "unknown tool: NAME"; an exception gives an
    error result with the exception message."""
    raise NotImplementedError("Your turn: write this one")


def agent_loop(client, user_message: str, tools: list[dict], registry: dict, max_steps: int = 5) -> str:
    """Run the agent loop. Send the user message with `tools` (model MODEL, max_tokens 1024). While the
    reply's stop_reason is "tool_use": append the assistant reply (role "assistant", content =
    response.content), run the tools, append one user message holding all the tool_result blocks, and
    call again. Return the final reply's text. Raise RuntimeError if Claude still wants tools after
    `max_steps` calls."""
    raise NotImplementedError("Your turn: write this one")
