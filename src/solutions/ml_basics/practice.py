"""ML basics practice: scaling, encoding, a first classifier, and how training actually moves weights."""

import math
from collections import Counter


def z_score(values: list[float]) -> list[float]:
    """Standardise `values`: subtract the mean and divide by the population standard deviation. If the
    deviation is 0, return all zeros."""
    n = len(values)
    mean = sum(values) / n
    std = (sum((v - mean) ** 2 for v in values) / n) ** 0.5
    if std == 0:
        return [0.0] * n
    return [(v - mean) / std for v in values]


def one_hot(labels: list[str]) -> tuple[list[str], list[list[int]]]:
    """Turn category labels into one-hot vectors. Return (classes, vectors) where classes is the sorted
    list of distinct labels and each vector has a 1 at its label's position."""
    # Models need numbers. One-hot avoids implying an order ("red" < "green") that integers would.
    classes = sorted(set(labels))
    index = {c: i for i, c in enumerate(classes)}
    vectors = []
    for label in labels:
        v = [0] * len(classes)
        v[index[label]] = 1
        vectors.append(v)
    return classes, vectors


def mse_loss(y_true: list[float], y_pred: list[float]) -> float:
    """Return the mean squared error between the true and predicted values."""
    return sum((t - p) ** 2 for t, p in zip(y_true, y_pred)) / len(y_true)


def knn_predict(points: list[list[float]], labels: list[str], query: list[float], k: int) -> str:
    """k-nearest neighbours: find the k training points closest to `query` (Euclidean distance) and
    return the most common label among them. Break a tie in votes with the label of the nearest point
    among the tied labels."""
    # No training step at all: the "model" is the data. Prediction cost grows with the data set.
    by_distance = sorted(range(len(points)), key=lambda i: math.dist(points[i], query))[:k]
    votes = Counter(labels[i] for i in by_distance)
    best = max(votes.values())
    tied = {label for label, c in votes.items() if c == best}
    for i in by_distance:  # nearest first
        if labels[i] in tied:
            return labels[i]
    raise AssertionError("unreachable")


def gradient_descent_step(w: float, b: float, xs: list[float], ys: list[float], lr: float) -> tuple[float, float]:
    """Do one step of gradient descent for y = w * x + b with mean squared error loss. Return the new
    (w, b)."""
    # Gradient of MSE: dL/dw = 2/n * sum((pred - y) * x), dL/db = 2/n * sum(pred - y).
    # Step against the gradient, scaled by the learning rate. Training is just this, repeated.
    n = len(xs)
    errors = [(w * x + b) - y for x, y in zip(xs, ys)]
    dw = 2 / n * sum(e * x for e, x in zip(errors, xs))
    db = 2 / n * sum(errors)
    return w - lr * dw, b - lr * db


def logistic_predict(weights: list[float], bias: float, x: list[float], threshold: float = 0.5) -> tuple[float, int]:
    """Logistic regression: squash the linear score through the sigmoid 1 / (1 + e^-z). Return the
    probability and the class, 1 if the probability is at least `threshold`, else 0."""
    z = sum(w * xi for w, xi in zip(weights, x)) + bias
    p = 1 / (1 + math.exp(-z))
    return p, int(p >= threshold)


def k_fold_indices(n: int, k: int) -> list[tuple[list[int], list[int]]]:
    """Split indices 0..n-1 into k folds of consecutive indices (the first n % k folds get one extra).
    Return k (train_indices, test_indices) pairs, where each fold is the test set once."""
    # Cross-validation: every row is tested exactly once, so one lucky split can't fool you.
    sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
    folds, start = [], 0
    for size in sizes:
        test = list(range(start, start + size))
        train = [i for i in range(n) if not start <= i < start + size]
        folds.append((train, test))
        start += size
    return folds
