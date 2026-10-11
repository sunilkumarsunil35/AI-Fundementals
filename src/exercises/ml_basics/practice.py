# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k ml_basics
# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/ml_basics/practice.py

"""ML basics practice: scaling, encoding, a first classifier, and how training actually moves weights."""

import math
from collections import Counter


def z_score(values: list[float]) -> list[float]:
    """Standardise `values`: subtract the mean and divide by the population standard deviation. If the
    deviation is 0, return all zeros."""
    raise NotImplementedError("Your turn: write this one")


def one_hot(labels: list[str]) -> tuple[list[str], list[list[int]]]:
    """Turn category labels into one-hot vectors. Return (classes, vectors) where classes is the sorted
    list of distinct labels and each vector has a 1 at its label's position."""
    raise NotImplementedError("Your turn: write this one")


def mse_loss(y_true: list[float], y_pred: list[float]) -> float:
    """Return the mean squared error between the true and predicted values."""
    raise NotImplementedError("Your turn: write this one")


def knn_predict(points: list[list[float]], labels: list[str], query: list[float], k: int) -> str:
    """k-nearest neighbours: find the k training points closest to `query` (Euclidean distance) and
    return the most common label among them. Break a tie in votes with the label of the nearest point
    among the tied labels."""
    raise NotImplementedError("Your turn: write this one")


def gradient_descent_step(w: float, b: float, xs: list[float], ys: list[float], lr: float) -> tuple[float, float]:
    """Do one step of gradient descent for y = w * x + b with mean squared error loss. Return the new
    (w, b)."""
    raise NotImplementedError("Your turn: write this one")


def logistic_predict(weights: list[float], bias: float, x: list[float], threshold: float = 0.5) -> tuple[float, int]:
    """Logistic regression: squash the linear score through the sigmoid 1 / (1 + e^-z). Return the
    probability and the class, 1 if the probability is at least `threshold`, else 0."""
    raise NotImplementedError("Your turn: write this one")


def k_fold_indices(n: int, k: int) -> list[tuple[list[int], list[int]]]:
    """Split indices 0..n-1 into k folds of consecutive indices (the first n % k folds get one extra).
    Return k (train_indices, test_indices) pairs, where each fold is the test set once."""
    raise NotImplementedError("Your turn: write this one")
