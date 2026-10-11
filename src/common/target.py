"""Picks which code the tests check: the worked solutions, or your own exercises.

`sh run-tests.sh` checks src/solutions. `sh run-tests.sh --mine` checks src/exercises, the files
you fill in yourself.
"""

import importlib
import os


def load(topic, kind):
    """Import <package>.<topic>.<kind>, where kind is "problems" or "practice"."""
    package = "exercises" if os.environ.get("AI_TARGET") == "exercises" else "solutions"
    return importlib.import_module(f"{package}.{topic}.{kind}")
