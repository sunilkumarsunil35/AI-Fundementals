"""Tool use and agents: let Claude call your functions, and keep the loop safe and testable.

Claude never runs your code. It replies with a tool_use block naming a tool and its input; you run
it and send back a tool_result. An agent is that exchange in a loop, until Claude stops asking.
"""

MODEL = "claude-opus-5-5"


def make_tool(name: str, description: str, params: dict[str, tuple[str, str]], required: list[str]) -> dict:
    """Build a Claude tool definition: {"name", "description", "input_schema"} where input_schema is
    {"type": "object", "properties": {param: {"type": type, "description": desc}}, "required": required}.
    `params` maps each parameter name to (json type, description)."""
    # The description is a prompt: say what the tool does, when to use it, and what it returns.
    return {
        "name": name,
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": {p: {"type": t, "description": d} for p, (t, d) in params.items()},
            "required": required,
        },
    }


def tool_calls(response) -> list[tuple[str, str, dict]]:
    """Return (id, name, input) for every block of type "tool_use" in response.content, in order."""
    # One reply can hold several tool_use blocks (parallel tool calls). Handle them all.
    return [(b.id, b.name, b.input) for b in response.content if b.type == "tool_use"]


def tool_result(tool_use_id: str, output, is_error: bool = False) -> dict:
    """Build a tool_result block: {"type": "tool_result", "tool_use_id": ..., "content": str(output)},
    plus "is_error": True when is_error is set."""
    block = {"type": "tool_result", "tool_use_id": tool_use_id, "content": str(output)}
    if is_error:
        block["is_error"] = True
    return block


def execute_tool_calls(response, registry: dict) -> list[dict]:
    """Run every tool call in `response` with registry[name](**input) and return one tool_result per
    call, in order. An unknown tool gives an error result "unknown tool: NAME"; an exception gives an
    error result with the exception message."""
    # Never drop a failed call: send is_error back so Claude can recover (try other input, apologise).
    results = []
    for id, name, inp in tool_calls(response):
        fn = registry.get(name)
        if fn is None:
            results.append(tool_result(id, f"unknown tool: {name}", True))
            continue
        try:
            results.append(tool_result(id, fn(**inp)))
        except Exception as e:
            results.append(tool_result(id, str(e), True))
    return results


def agent_loop(client, user_message: str, tools: list[dict], registry: dict, max_steps: int = 5) -> str:
    """Run the agent loop. Send the user message with `tools` (model MODEL, max_tokens 1024). While the
    reply's stop_reason is "tool_use": append the assistant reply (role "assistant", content =
    response.content), run the tools, append one user message holding all the tool_result blocks, and
    call again. Return the final reply's text. Raise RuntimeError if Claude still wants tools after
    `max_steps` calls."""
    # max_steps is a guard rail: a confused agent can loop forever and burn money.
    messages = [{"role": "user", "content": user_message}]
    for _ in range(max_steps):
        response = client.messages.create(model=MODEL, max_tokens=1024, tools=tools, messages=messages)
        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": execute_tool_calls(response, registry)})
    raise RuntimeError(f"agent did not finish in {max_steps} steps")
