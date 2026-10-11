# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k metrics
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/metrics/practice.py

"""Metrics practice: multi-class scores and the text metrics used to grade LLM answers."""

import re
import string
from collections import Counter
from math import comb


def confusion_matrix(y_true: list, y_pred: list, labels: list) -> list[list[int]]:
    """Return a square matrix where row i is the true label labels[i] and column j is the predicted
    label labels[j], each cell counting how often that pair happened."""
    raise NotImplementedError("Your turn: write this one")


def macro_f1(y_true: list, y_pred: list) -> float:
    """Return the F1 averaged over every label that appears in y_true or y_pred, each label weighted
    equally."""
    raise NotImplementedError("Your turn: write this one")


def normalize_answer(text: str) -> str:
    """Normalise an answer for comparison: lower case, remove punctuation, remove the articles a, an and
    the, and collapse whitespace to single spaces."""
    raise NotImplementedError("Your turn: write this one")


def exact_match(prediction: str, reference: str) -> bool:
    """Return True if the two answers match after normalising both: lower case, no punctuation, no
    articles (a, an, the) and single spaces."""
    raise NotImplementedError("Your turn: write this one")


def token_f1(prediction: str, reference: str) -> float:
    """Return the F1 of the overlapping words between the normalised prediction and reference
    (counting repeated words as often as they appear in both). 0.0 if either is empty."""
    raise NotImplementedError("Your turn: write this one")


def rouge_l(prediction: str, reference: str) -> float:
    """ROUGE-L: the F1 built from the longest common subsequence of words (lower-cased, split on
    spaces) between prediction and reference. 0.0 if either is empty."""
    raise NotImplementedError("Your turn: write this one")


def best_threshold(scores: list[float], labels: list[int], thresholds: list[float]) -> float:
    """Each score is a model's confidence that the label is 1. For each threshold, predict 1 when
    score >= threshold, and return the threshold with the highest F1 (the first one on a tie)."""
    raise NotImplementedError("Your turn: write this one")


def pass_at_k(n: int, c: int, k: int) -> float:
    """pass@k: you sampled n answers and c of them were correct. Return the chance that at least one of
    k answers drawn at random from those n is correct: 1 - C(n - c, k) / C(n, k)."""
    raise NotImplementedError("Your turn: write this one")
