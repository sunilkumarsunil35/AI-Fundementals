# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k metrics
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/metrics/problems.py

"""Evaluation metrics: how you know a model (or an LLM feature) is good enough to ship.

For an SDET these are the assertions of AI testing. "The model works" means nothing; "precision is
0.93 on the golden set, up from 0.89" is a test result.
"""

import math


def accuracy(y_true: list, y_pred: list) -> float:
    """Return the fraction of predictions that equal the true label."""
    raise NotImplementedError("Your turn: write this one")


def confusion_counts(y_true: list, y_pred: list, positive) -> dict:
    """Count true positives, false positives, false negatives and true negatives for the class
    `positive`. Return {"tp": .., "fp": .., "fn": .., "tn": ..}."""
    raise NotImplementedError("Your turn: write this one")


def precision_recall_f1(y_true: list, y_pred: list, positive) -> tuple[float, float, float]:
    """Return (precision, recall, f1) for the class `positive`. Any ratio with a zero denominator is 0.0."""
    raise NotImplementedError("Your turn: write this one")


def mae_rmse(y_true: list[float], y_pred: list[float]) -> tuple[float, float]:
    """Return the mean absolute error and the root mean squared error."""
    raise NotImplementedError("Your turn: write this one")
