"""Evaluation metrics: how you know a model (or an LLM feature) is good enough to ship.

For an SDET these are the assertions of AI testing. "The model works" means nothing; "precision is
0.93 on the golden set, up from 0.89" is a test result.
"""

import math


def accuracy(y_true: list, y_pred: list) -> float:
    """Return the fraction of predictions that equal the true label."""
    return sum(t == p for t, p in zip(y_true, y_pred)) / len(y_true)


def confusion_counts(y_true: list, y_pred: list, positive) -> dict:
    """Count true positives, false positives, false negatives and true negatives for the class
    `positive`. Return {"tp": .., "fp": .., "fn": .., "tn": ..}."""
    c = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    for t, p in zip(y_true, y_pred):
        if p == positive:
            c["tp" if t == positive else "fp"] += 1
        else:
            c["fn" if t == positive else "tn"] += 1
    return c


def precision_recall_f1(y_true: list, y_pred: list, positive) -> tuple[float, float, float]:
    """Return (precision, recall, f1) for the class `positive`. Any ratio with a zero denominator is 0.0."""
    # Precision: of what I flagged, how much was right? Recall: of what was there, how much did I find?
    # F1 is their harmonic mean, so it is low if either one is low.
    c = confusion_counts(y_true, y_pred, positive)
    precision = c["tp"] / (c["tp"] + c["fp"]) if c["tp"] + c["fp"] else 0.0
    recall = c["tp"] / (c["tp"] + c["fn"]) if c["tp"] + c["fn"] else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def mae_rmse(y_true: list[float], y_pred: list[float]) -> tuple[float, float]:
    """Return the mean absolute error and the root mean squared error."""
    # RMSE punishes big misses more than MAE does. If RMSE >> MAE, a few predictions are way off.
    n = len(y_true)
    mae = sum(abs(t - p) for t, p in zip(y_true, y_pred)) / n
    rmse = math.sqrt(sum((t - p) ** 2 for t, p in zip(y_true, y_pred)) / n)
    return mae, rmse
