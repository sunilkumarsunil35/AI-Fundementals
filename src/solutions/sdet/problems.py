"""AI in the SDET process: using Claude across the test life cycle, with code that checks its work.

Requirements -> test design -> test data -> automation -> execution -> triage. Claude drafts; your code
parses, validates, de-duplicates and decides. Never paste model output straight into a test suite.
"""

import re

MODEL = "claude-opus-5-5"


def boundary_values(low: int, high: int) -> list[int]:
    """Boundary value analysis for a valid range low..high: return [low - 1, low, low + 1, high - 1, high,
    high + 1], without duplicates, in that order."""
    out = []
    for v in (low - 1, low, low + 1, high - 1, high, high + 1):
        if v not in out:
            out.append(v)
    return out


def test_case_prompt(requirement: str, count: int) -> str:
    """Build a prompt asking Claude for `count` test cases for the requirement, as a markdown table with
    exactly the columns | ID | Title | Steps | Expected |, covering positive, negative and boundary cases.
    Put the requirement inside <requirement> tags."""
    # Fix the output format in the prompt so parse_test_cases() can rely on it.
    return (
        f"<requirement>{requirement}</requirement>\n"
        f"Write {count} test cases for this requirement, covering positive, negative and boundary cases.\n"
        "Reply with only a markdown table with exactly these columns: | ID | Title | Steps | Expected |"
    )


def parse_test_cases(markdown: str) -> list[dict]:
    """Parse a markdown table into a list of dicts keyed by the header cells (stripped). Skip the
    |---|---| separator row and any line that is not a table row. Ignore text around the table."""
    rows = [line.strip() for line in markdown.splitlines() if line.strip().startswith("|")]
    if not rows:
        return []
    cells = lambda line: [c.strip() for c in line.strip("|").split("|")]
    header = cells(rows[0])
    out = []
    for line in rows[1:]:
        values = cells(line)
        if all(re.fullmatch(r":?-+:?", v) for v in values):
            continue
        out.append(dict(zip(header, values)))
    return out


def flaky_tests(history: dict[str, list[str]], min_flips: int = 2) -> list[str]:
    """`history` maps a test name to its recent results ("pass"/"fail"), oldest first. A flip is a change
    between consecutive results. Return the sorted names with at least `min_flips` flips."""
    # A test that alternates is flaky; a test that went pass -> fail once and stayed red is a real bug.
    return sorted(t for t, runs in history.items() if sum(a != b for a, b in zip(runs, runs[1:])) >= min_flips)


def failure_signature(message: str) -> str:
    """Normalise an error message so the same failure groups together: replace hex ids (0x...) and long
    hex strings (8+ hex chars) with <ID>, numbers with <N>, quoted strings with <S>, and collapse
    whitespace."""
    s = re.sub(r"0x[0-9a-fA-F]+|\b[0-9a-f]{8,}\b", "<ID>", message)
    s = re.sub(r"(['\"]).*?\1", "<S>", s)
    s = re.sub(r"\d+", "<N>", s)
    return " ".join(s.split())


def group_failures(failures: dict[str, str]) -> dict[str, list[str]]:
    """`failures` maps a test name to its error message. Group the test names (sorted) by
    failure_signature(message)."""
    # 200 red tests with 3 signatures = 3 bugs to look at, not 200. Send each group to Claude for triage.
    groups = {}
    for test in sorted(failures):
        groups.setdefault(failure_signature(failures[test]), []).append(test)
    return groups
