"""Run some of the worked solutions against the real Claude API, to see the same code that the tests
check with FakeClaude working live.

    pip install -r requirements-claude.txt
    export ANTHROPIC_API_KEY=...        # or sign in once with: ant auth login
    python scripts/try_with_claude.py            # the worked solutions
    python scripts/try_with_claude.py --mine     # your own code in src/exercises

Each call costs a fraction of a cent. Nothing here runs in CI.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
if "--mine" in sys.argv:
    os.environ["AI_TARGET"] = "exercises"

from common.claude import get_client  # noqa: E402
from common.target import load  # noqa: E402


def main():
    client = get_client()
    prompts = load("prompts", "problems")
    prompts_practice = load("prompts", "practice")
    judge = load("llm_testing", "practice")
    rag = load("rag", "problems")
    agents = load("agents", "problems")
    sdet = load("sdet", "practice")

    print("1. ask_claude:")
    print("  ", prompts.ask_claude(client, "In one sentence: why is testing LLM output harder than testing a REST API?"))

    print("2. classify:")
    print("  ", prompts_practice.classify(client, "Checkout button does nothing on Safari", ["bug", "feature_request", "question"]))

    print("3. llm_judge:")
    print("  ", judge.llm_judge(client, "What is a flaky test?", "A test that sometimes passes and sometimes fails on the same code.",
                                "5 = correct and mentions the code didn't change; 1 = wrong"))

    print("4. answer_with_rag:")
    docs = {"refunds": "Refunds are issued within 5 days of a return. Contact support for late refunds.",
            "shipping": "Standard shipping takes 3 days. Express shipping takes 1 day."}
    text, cited = rag.answer_with_rag(client, "How long does express shipping take?", rag.split_documents(docs, 8, 2), 2)
    print("  ", text, "| cited:", cited)

    print("5. agent_loop:")
    tool = agents.make_tool("get_test_results", "Get the latest pass/fail counts for a test suite.",
                            {"suite": ("string", "Suite name, like 'checkout'")}, ["suite"])
    results = {"checkout": "41 passed, 3 failed", "login": "12 passed, 0 failed"}
    print("  ", agents.agent_loop(client, "How is the checkout suite doing?", [tool],
                                  {"get_test_results": lambda suite: results.get(suite, "unknown suite")}))

    print("6. triage:")
    print("  ", sdet.triage(client, "test_payment", "requests.exceptions.ConnectionError: Failed to resolve 'payments.staging.local'"))


if __name__ == "__main__":
    main()
