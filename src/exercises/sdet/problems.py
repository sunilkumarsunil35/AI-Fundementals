# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k sdet
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/sdet/problems.py

"""AI in the SDET process: using Claude across the test life cycle, with code that checks its work.

Requirements -> test design -> test data -> automation -> execution -> triage. Claude drafts; your code
parses, validates, de-duplicates and decides. Never paste model output straight into a test suite.
"""

import re

MODEL = "claude-opus-5-5"


def boundary_values(low: int, high: int) -> list[int]:
    """Boundary value analysis for a valid range low..high: return [low - 1, low, low + 1, high - 1, high,
    high + 1], without duplicates, in that order."""
    raise NotImplementedError("Your turn: write this one")


def test_case_prompt(requirement: str, count: int) -> str:
    """Build a prompt asking Claude for `count` test cases for the requirement, as a markdown table with
    exactly the columns | ID | Title | Steps | Expected |, covering positive, negative and boundary cases.
    Put the requirement inside <requirement> tags."""
    raise NotImplementedError("Your turn: write this one")


def parse_test_cases(markdown: str) -> list[dict]:
    """Parse a markdown table into a list of dicts keyed by the header cells (stripped). Skip the
    |---|---| separator row and any line that is not a table row. Ignore text around the table."""
    raise NotImplementedError("Your turn: write this one")


def flaky_tests(history: dict[str, list[str]], min_flips: int = 2) -> list[str]:
    """`history` maps a test name to its recent results ("pass"/"fail"), oldest first. A flip is a change
    between consecutive results. Return the sorted names with at least `min_flips` flips."""
    raise NotImplementedError("Your turn: write this one")


def failure_signature(message: str) -> str:
    """Normalise an error message so the same failure groups together: replace hex ids (0x...) and long
    hex strings (8+ hex chars) with <ID>, numbers with <N>, quoted strings with <S>, and collapse
    whitespace."""
    raise NotImplementedError("Your turn: write this one")


def group_failures(failures: dict[str, str]) -> dict[str, list[str]]:
    """`failures` maps a test name to its error message. Group the test names (sorted) by
    failure_signature(message)."""
    raise NotImplementedError("Your turn: write this one")
