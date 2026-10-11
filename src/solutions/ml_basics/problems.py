"""ML basics: the vocabulary under every AI system: data, features, training, prediction.

No libraries, only plain Python lists, so you see every step. Once it makes sense, the same ideas
in NumPy or scikit-learn are one line each.
"""

import random


def mean_and_std(values: list[float]) -> tuple[float, float]:
    """Return the mean and the population standard deviation of `values`."""
    # std = sqrt(average squared distance from the mean). "Population" divides by n, not n - 1.
    n = len(values)
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / n
    return mean, variance ** 0.5


def min_max_scale(values: list[float]) -> list[float]:
    """Rescale `values` into the range 0..1: the smallest becomes 0, the largest 1. If every value is
    the same, return all zeros."""
    # Features on very different scales (age vs salary) confuse distance-based models like kNN.
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.0] * len(values)
    return [(v - lo) / (hi - lo) for v in values]


def train_test_split(rows: list, test_ratio: float, seed: int) -> tuple[list, list]:
    """Shuffle a copy of `rows` with random.Random(seed), then put the first round(len * test_ratio)
    rows in the test set and the rest in the training set. Return (train, test)."""
    # A fixed seed makes the split repeatable: the same rows land in test on every run, so a failing
    # model test is reproducible. Never shuffle the caller's list in place.
    shuffled = list(rows)
    random.Random(seed).shuffle(shuffled)
    n_test = round(len(shuffled) * test_ratio)
    return shuffled[n_test:], shuffled[:n_test]


def predict_linear(weights: list[float], bias: float, x: list[float]) -> float:
    """Return the prediction of a linear model: the dot product of `weights` and `x`, plus `bias`."""
    # Every neural network layer is this, followed by a non-linear function.
    return sum(w * xi for w, xi in zip(weights, x)) + bias


def fit_line(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """Fit y = slope * x + intercept by least squares and return (slope, intercept)."""
    # Closed form: slope = cov(x, y) / var(x); the line passes through (mean x, mean y).
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    var = sum((x - mx) ** 2 for x in xs)
    slope = cov / var
    return slope, my - slope * mx
