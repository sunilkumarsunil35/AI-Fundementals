from pytest import approx

from common.target import load

P = load("metrics", "problems")

TRUE = ["spam", "spam", "ham", "ham", "spam", "ham"]
PRED = ["spam", "ham", "ham", "spam", "spam", "ham"]


def test_accuracy():
    assert P.accuracy(TRUE, PRED) == approx(4 / 6)


def test_confusion_counts():
    assert P.confusion_counts(TRUE, PRED, "spam") == {"tp": 2, "fp": 1, "fn": 1, "tn": 2}


def test_precision_recall_f1():
    assert P.precision_recall_f1(TRUE, PRED, "spam") == approx((2 / 3, 2 / 3, 2 / 3))
    assert P.precision_recall_f1(["a"], ["b"], "c") == (0.0, 0.0, 0.0)


def test_mae_rmse():
    assert P.mae_rmse([3, 5, 2], [2, 5, 4]) == approx((1.0, (5 / 3) ** 0.5))
