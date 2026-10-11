"""Testing LLM apps: the heart of the AI SDET job.

LLM output is non-deterministic and free text, so `assert reply == expected` fails. Instead you check
properties (keywords, schema, length), run golden data sets, measure consistency, retry transient
errors and let a second model grade the first.
"""

import re
from collections import Counter
from typing import Callable

RETRYABLE = {408, 409, 429, 500, 502, 503, 504, 529}


def missing_keywords(text: str, keywords: list[str]) -> list[str]:
    """Return the keywords that do not appear in `text` (case-insensitive), in their original order."""
    low = text.lower()
    return [k for k in keywords if k.lower() not in low]


def run_golden_set(fn: Callable[[str], str], cases: list[dict]) -> dict:
    """Run `fn` on each case's "input" and check that the output contains every keyword in the case's
    "expected" list (case-insensitive). Return {"passed": n, "failed": n, "failures": [ids of failed
    cases]}. A case whose fn call raises counts as failed."""
    # A golden set is your regression suite for prompts: rerun it on every prompt or model change.
    report = {"passed": 0, "failed": 0, "failures": []}
    for case in cases:
        try:
            ok = not missing_keywords(fn(case["input"]), case["expected"])
        except Exception:
            ok = False
        if ok:
            report["passed"] += 1
        else:
            report["failed"] += 1
            report["failures"].append(case["id"])
    return report


def consistency_rate(fn: Callable[[str], str], prompt: str, runs: int) -> float:
    """Call fn(prompt) `runs` times. Compare answers after stripping and lower-casing. Return the
    fraction of runs that gave the most common answer."""
    # 1.0 = stable. 0.6 = the feature is flaky and a single passing run proves nothing.
    answers = Counter(fn(prompt).strip().lower() for _ in range(runs))
    return answers.most_common(1)[0][1] / runs


def call_with_retry(fn: Callable[[], object], retries: int, base_delay: float, sleep: Callable[[float], None]):
    """Call fn(). If it raises an exception whose `status_code` is in RETRYABLE, sleep base_delay * 2**n
    (n = 0, 1, 2...) and try again, up to `retries` retries. Re-raise anything else at once, and the last
    error when retries run out."""
    # 429 (rate limit) and 529 (overloaded) are normal under load. 400 means your request is wrong;
    # retrying it only wastes money. `sleep` is injected so tests don't actually wait.
    for attempt in range(retries + 1):
        try:
            return fn()
        except Exception as e:
            if getattr(e, "status_code", None) not in RETRYABLE or attempt == retries:
                raise
            sleep(base_delay * 2 ** attempt)


def parse_judge_score(text: str) -> int:
    """Read a 1-5 score from a judge model's reply. Accept "<score>4</score>" or "Score: 4" (any case).
    Raise ValueError if there is no score or it is outside 1-5."""
    m = re.search(r"<score>\s*(\d+)\s*</score>", text) or re.search(r"score\s*[:=]\s*(\d+)", text, re.I)
    if not m:
        raise ValueError("no score in judge reply")
    score = int(m.group(1))
    if not 1 <= score <= 5:
        raise ValueError(f"score {score} out of range")
    return score
