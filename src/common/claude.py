"""The real Claude client, for scripts/try_with_claude.py. Tests never import this.

Install with `pip install -r requirements-claude.txt` and set ANTHROPIC_API_KEY (or sign in with
`ant auth login`). Every function in the exercises takes a `client`, so you can pass this one in.
"""

MODEL = "claude-opus-5-5"


def get_client():
    try:
        import anthropic
    except ImportError as e:  # pragma: no cover
        raise SystemExit("pip install -r requirements-claude.txt first") from e
    return anthropic.Anthropic()
