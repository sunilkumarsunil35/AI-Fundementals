# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k ml_basics
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/ml_basics/problems.py

"""ML basics: the vocabulary under every AI system: data, features, training, prediction.

No libraries, only plain Python lists, so you see every step. Once it makes sense, the same ideas
in NumPy or scikit-learn are one line each.
"""

import random


def mean_and_std(values: list[float]) -> tuple[float, float]:
    """Return the mean and the population standard deviation of `values`."""
    raise NotImplementedError("Your turn: write this one")


def min_max_scale(values: list[float]) -> list[float]:
    """Rescale `values` into the range 0..1: the smallest becomes 0, the largest 1. If every value is
    the same, return all zeros."""
    raise NotImplementedError("Your turn: write this one")


def train_test_split(rows: list, test_ratio: float, seed: int) -> tuple[list, list]:
    """Shuffle a copy of `rows` with random.Random(seed), then put the first round(len * test_ratio)
    rows in the test set and the rest in the training set. Return (train, test)."""
    raise NotImplementedError("Your turn: write this one")


def predict_linear(weights: list[float], bias: float, x: list[float]) -> float:
    """Return the prediction of a linear model: the dot product of `weights` and `x`, plus `bias`."""
    raise NotImplementedError("Your turn: write this one")


def fit_line(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """Fit y = slope * x + intercept by least squares and return (slope, intercept)."""
    raise NotImplementedError("Your turn: write this one")
