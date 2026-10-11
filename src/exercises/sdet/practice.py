# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k sdet
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/sdet/practice.py

"""SDET practice: pairwise design, self-healing locators, risk-based selection, Gherkin, seeded test
data and Claude-assisted triage."""

import itertools
import random
import re

MODEL = "claude-opus-5-5"
TRIAGE_LABELS = ["product_bug", "test_bug", "environment", "flaky"]


def pairwise(params: dict[str, list]) -> list[dict]:
    """All-pairs test design: return a list of test combinations (dicts of param -> value) such that every
    pair of values of every two parameters appears in at least one test. Greedy: start from the full
    cartesian product in order and repeatedly take the combination covering the most uncovered pairs
    (the first one on a tie) until every pair is covered."""
    raise NotImplementedError("Your turn: write this one")


def heal_locator(old: dict[str, str], candidates: list[dict[str, str]]) -> int:
    """Self-healing locator: the element described by `old` (attributes like id, text, role, class) is
    gone. Score each candidate by how many of old's attributes it matches exactly (the "id" attribute
    counts 3, "text" counts 2, others 1). Return the index of the best candidate, or -1 if none scores
    above 0. Ties go to the earlier candidate."""
    raise NotImplementedError("Your turn: write this one")


def prioritize(tests: dict[str, dict], changed_files: set[str]) -> list[str]:
    """Each test has {"covers": [files], "recent_failures": n}. Risk = 2 * (number of changed files it
    covers) + recent_failures. Return the names of tests with risk > 0, highest first, ties by name."""
    raise NotImplementedError("Your turn: write this one")


def parse_gherkin(text: str) -> dict:
    """Parse Gherkin into {"feature": name, "scenarios": [{"name": .., "steps": [..]}]}. Lines start with
    "Feature:", "Scenario:" or a step keyword (Given, When, Then, And, But); keep each step line
    stripped. Ignore other lines."""
    raise NotImplementedError("Your turn: write this one")


def generate_test_data(schema: dict[str, dict], n: int, seed: int) -> list[dict]:
    """Make `n` rows with random.Random(seed). For each field (in schema order): {"type": "int", "min",
    "max"} -> rng.randint(min, max); {"type": "choice", "values"} -> rng.choice(values); {"type":
    "email"} -> "user<k>@example.com" where k is the row number from 1."""
    raise NotImplementedError("Your turn: write this one")


def triage(client, test_name: str, log: str) -> str:
    """Ask Claude to classify a failed test as one of TRIAGE_LABELS, giving the test name and log in
    <test> and <log> tags and asking for the answer inside <category></category> tags. Return the
    category, or "needs_human" if the reply has no valid one."""
    raise NotImplementedError("Your turn: write this one")


def review_generated_tests(cases: list[dict]) -> list[str]:
    """Review test cases a model wrote (dicts with ID, Title, Steps, Expected). Return problems as
    strings: "<ID>: missing <field>" for an empty or absent field, "<ID>: duplicate title" when the title
    (case-insensitive) already appeared, and "<ID>: vague expected" when Expected is one of "works",
    "ok", "as expected", "success" (case-insensitive)."""
    raise NotImplementedError("Your turn: write this one")
