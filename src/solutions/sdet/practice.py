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
    # 4 params x 3 values = 81 full combinations; pairwise covers every pair in about 9-10.
    names = list(params)
    def pairs_of(combo):
        return {((a, combo[a]), (b, combo[b])) for a, b in itertools.combinations(names, 2)}
    all_combos = [dict(zip(names, values)) for values in itertools.product(*params.values())]
    uncovered = set().union(*(pairs_of(c) for c in all_combos)) if len(names) > 1 else set()
    chosen = []
    if not uncovered:
        return all_combos
    while uncovered:
        best = max(all_combos, key=lambda c: len(pairs_of(c) & uncovered))
        chosen.append(best)
        uncovered -= pairs_of(best)
    return chosen


def heal_locator(old: dict[str, str], candidates: list[dict[str, str]]) -> int:
    """Self-healing locator: the element described by `old` (attributes like id, text, role, class) is
    gone. Score each candidate by how many of old's attributes it matches exactly (the "id" attribute
    counts 3, "text" counts 2, others 1). Return the index of the best candidate, or -1 if none scores
    above 0. Ties go to the earlier candidate."""
    weights = {"id": 3, "text": 2}
    best, best_score = -1, 0
    for i, cand in enumerate(candidates):
        score = sum(weights.get(k, 1) for k, v in old.items() if cand.get(k) == v)
        if score > best_score:
            best, best_score = i, score
    return best


def prioritize(tests: dict[str, dict], changed_files: set[str]) -> list[str]:
    """Each test has {"covers": [files], "recent_failures": n}. Risk = 2 * (number of changed files it
    covers) + recent_failures. Return the names of tests with risk > 0, highest first, ties by name."""
    risk = {n: 2 * len(set(t["covers"]) & changed_files) + t["recent_failures"] for n, t in tests.items()}
    return sorted((n for n in risk if risk[n] > 0), key=lambda n: (-risk[n], n))


def parse_gherkin(text: str) -> dict:
    """Parse Gherkin into {"feature": name, "scenarios": [{"name": .., "steps": [..]}]}. Lines start with
    "Feature:", "Scenario:" or a step keyword (Given, When, Then, And, But); keep each step line
    stripped. Ignore other lines."""
    out = {"feature": "", "scenarios": []}
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("Feature:"):
            out["feature"] = line[len("Feature:"):].strip()
        elif line.startswith("Scenario:"):
            out["scenarios"].append({"name": line[len("Scenario:"):].strip(), "steps": []})
        elif re.match(r"(Given|When|Then|And|But)\b", line) and out["scenarios"]:
            out["scenarios"][-1]["steps"].append(line)
    return out


def generate_test_data(schema: dict[str, dict], n: int, seed: int) -> list[dict]:
    """Make `n` rows with random.Random(seed). For each field (in schema order): {"type": "int", "min",
    "max"} -> rng.randint(min, max); {"type": "choice", "values"} -> rng.choice(values); {"type":
    "email"} -> "user<k>@example.com" where k is the row number from 1."""
    # Seeded data: random enough to find bugs, repeatable enough to debug them.
    rng = random.Random(seed)
    rows = []
    for k in range(1, n + 1):
        row = {}
        for field, spec in schema.items():
            if spec["type"] == "int":
                row[field] = rng.randint(spec["min"], spec["max"])
            elif spec["type"] == "choice":
                row[field] = rng.choice(spec["values"])
            elif spec["type"] == "email":
                row[field] = f"user{k}@example.com"
        rows.append(row)
    return rows


def triage(client, test_name: str, log: str) -> str:
    """Ask Claude to classify a failed test as one of TRIAGE_LABELS, giving the test name and log in
    <test> and <log> tags and asking for the answer inside <category></category> tags. Return the
    category, or "needs_human" if the reply has no valid one."""
    # The model suggests; the label set is fixed and anything unexpected goes to a person.
    prompt = (
        f"<test>{test_name}</test>\n<log>{log}</log>\n"
        f"Classify this failure as one of: {', '.join(TRIAGE_LABELS)}. "
        "Answer inside <category></category> tags."
    )
    response = client.messages.create(model=MODEL, max_tokens=1024,
                                      messages=[{"role": "user", "content": prompt}])
    text = "".join(b.text for b in response.content if b.type == "text")
    m = re.search(r"<category>\s*(\w+)\s*</category>", text)
    return m.group(1) if m and m.group(1) in TRIAGE_LABELS else "needs_human"


def review_generated_tests(cases: list[dict]) -> list[str]:
    """Review test cases a model wrote (dicts with ID, Title, Steps, Expected). Return problems as
    strings: "<ID>: missing <field>" for an empty or absent field, "<ID>: duplicate title" when the title
    (case-insensitive) already appeared, and "<ID>: vague expected" when Expected is one of "works",
    "ok", "as expected", "success" (case-insensitive)."""
    # The human-in-the-loop step, partly automated: catch the lazy cases before a reviewer reads them.
    problems, seen = [], set()
    for c in cases:
        cid = c.get("ID", "?")
        for field in ("Title", "Steps", "Expected"):
            if not c.get(field, "").strip():
                problems.append(f"{cid}: missing {field}")
        title = c.get("Title", "").strip().lower()
        if title:
            if title in seen:
                problems.append(f"{cid}: duplicate title")
            seen.add(title)
        if c.get("Expected", "").strip().lower() in {"works", "ok", "as expected", "success"}:
            problems.append(f"{cid}: vague expected")
    return problems
