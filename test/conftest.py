"""Shared pytest setup.

- Adds `--mine`, which tests your code in src/exercises instead of src/solutions.
- Reports an exercise you have not written yet (it still raises NotImplementedError) as "todo"
  instead of a failure, and prints one line per topic at the end.
- Gives tests a `fake_claude` factory: FakeClaude from src/common, so nothing calls the real API.
"""

import os
from collections import defaultdict

import pytest

from common.fake_claude import FakeClaude


def pytest_addoption(parser):
    parser.addoption("--mine", action="store_true", help="test your own code in src/exercises")


def pytest_configure(config):
    if config.getoption("--mine"):
        os.environ["AI_TARGET"] = "exercises"


@pytest.fixture
def fake_claude():
    return FakeClaude


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when in ("setup", "call") and call.excinfo is not None and call.excinfo.errisinstance(NotImplementedError):
        report.outcome = "skipped"
        report.longrepr = (str(item.path), item.location[1] or 0, "todo: not written yet")
        report.todo = True


# Curriculum order, so the summary reads like the roadmap.
TOPICS = ["ml_basics", "metrics", "nlp", "embeddings", "prompts", "llm_testing", "rag", "agents", "guardrails", "sdet"]


def _order(name):
    base = name.removesuffix("_practice")
    return (TOPICS.index(base) if base in TOPICS else len(TOPICS), name)


PROGRESS = defaultdict(lambda: {"passed": 0, "failed": 0, "todo": 0})


def pytest_runtest_logreport(report):
    topic = report.nodeid.split("::")[0].rsplit("/", 1)[-1].removeprefix("test_").removesuffix(".py")
    if report.when == "call" or report.outcome != "passed":
        bucket = "todo" if report.skipped else "failed" if report.failed else "passed"
        PROGRESS[topic][bucket] += 1


def pytest_terminal_summary(terminalreporter):
    if not PROGRESS:
        return
    terminalreporter.section("progress by topic")
    for topic, c in sorted(PROGRESS.items(), key=lambda kv: _order(kv[0])):
        total = sum(c.values())
        state = "FAIL" if c["failed"] else "todo" if c["todo"] else "ok  "
        terminalreporter.write_line(f"{state} {topic:<22} {c['passed']}/{total} passing, {c['todo']} todo, {c['failed']} failed")
