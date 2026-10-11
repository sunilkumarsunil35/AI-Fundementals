"""Metrics practice: multi-class scores and the text metrics used to grade LLM answers."""

import re
import string
from collections import Counter
from math import comb


def confusion_matrix(y_true: list, y_pred: list, labels: list) -> list[list[int]]:
    """Return a square matrix where row i is the true label labels[i] and column j is the predicted
    label labels[j], each cell counting how often that pair happened."""
    index = {label: i for i, label in enumerate(labels)}
    m = [[0] * len(labels) for _ in labels]
    for t, p in zip(y_true, y_pred):
        m[index[t]][index[p]] += 1
    return m


def macro_f1(y_true: list, y_pred: list) -> float:
    """Return the F1 averaged over every label that appears in y_true or y_pred, each label weighted
    equally."""
    # Macro averaging stops a big easy class from hiding a small class the model always gets wrong.
    scores = []
    for label in sorted(set(y_true) | set(y_pred), key=str):
        tp = sum(t == label and p == label for t, p in zip(y_true, y_pred))
        fp = sum(t != label and p == label for t, p in zip(y_true, y_pred))
        fn = sum(t == label and p != label for t, p in zip(y_true, y_pred))
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        scores.append(2 * prec * rec / (prec + rec) if prec + rec else 0.0)
    return sum(scores) / len(scores)


def normalize_answer(text: str) -> str:
    """Normalise an answer for comparison: lower case, remove punctuation, remove the articles a, an and
    the, and collapse whitespace to single spaces."""
    text = text.lower()
    text = "".join(ch for ch in text if ch not in string.punctuation)
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    return " ".join(text.split())


def exact_match(prediction: str, reference: str) -> bool:
    """Return True if the two answers match after normalising both: lower case, no punctuation, no
    articles (a, an, the) and single spaces."""
    # LLMs say "The Eiffel Tower." when the reference is "eiffel tower". Normalise before comparing.
    return normalize_answer(prediction) == normalize_answer(reference)


def token_f1(prediction: str, reference: str) -> float:
    """Return the F1 of the overlapping words between the normalised prediction and reference
    (counting repeated words as often as they appear in both). 0.0 if either is empty."""
    # The SQuAD metric: partial credit for "Paris, France" against "Paris".
    pred, ref = normalize_answer(prediction).split(), normalize_answer(reference).split()
    if not pred or not ref:
        return 0.0
    common = sum((Counter(pred) & Counter(ref)).values())
    if common == 0:
        return 0.0
    precision, recall = common / len(pred), common / len(ref)
    return 2 * precision * recall / (precision + recall)


def rouge_l(prediction: str, reference: str) -> float:
    """ROUGE-L: the F1 built from the longest common subsequence of words (lower-cased, split on
    spaces) between prediction and reference. 0.0 if either is empty."""
    # LCS rewards words in the right order even with gaps, which suits summaries.
    a, b = prediction.lower().split(), reference.lower().split()
    if not a or not b:
        return 0.0
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a)):
        for j in range(len(b)):
            dp[i + 1][j + 1] = dp[i][j] + 1 if a[i] == b[j] else max(dp[i][j + 1], dp[i + 1][j])
    lcs = dp[-1][-1]
    if lcs == 0:
        return 0.0
    precision, recall = lcs / len(a), lcs / len(b)
    return 2 * precision * recall / (precision + recall)


def best_threshold(scores: list[float], labels: list[int], thresholds: list[float]) -> float:
    """Each score is a model's confidence that the label is 1. For each threshold, predict 1 when
    score >= threshold, and return the threshold with the highest F1 (the first one on a tie)."""
    best, best_f1 = thresholds[0], -1.0
    for th in thresholds:
        tp = sum(s >= th and y == 1 for s, y in zip(scores, labels))
        fp = sum(s >= th and y == 0 for s, y in zip(scores, labels))
        fn = sum(s < th and y == 1 for s, y in zip(scores, labels))
        f1 = 2 * tp / (2 * tp + fp + fn) if tp else 0.0
        if f1 > best_f1:
            best, best_f1 = th, f1
    return best


def pass_at_k(n: int, c: int, k: int) -> float:
    """pass@k: you sampled n answers and c of them were correct. Return the chance that at least one of
    k answers drawn at random from those n is correct: 1 - C(n - c, k) / C(n, k)."""
    # The standard metric for code generation: "if I let the model try k times, does one pass?"
    if n - c < k:
        return 1.0
    return 1 - comb(n - c, k) / comb(n, k)
