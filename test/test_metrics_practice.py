from pytest import approx

from common.target import load

P = load("metrics", "practice")


def test_confusion_matrix():
    m = P.confusion_matrix(["a", "b", "b", "c"], ["a", "b", "c", "c"], ["a", "b", "c"])
    assert m == [[1, 0, 0], [0, 1, 1], [0, 0, 1]]


def test_macro_f1():
    assert P.macro_f1(["a", "a", "b"], ["a", "a", "a"]) == approx((0.8 + 0.0) / 2)


def test_normalize_answer():
    assert P.normalize_answer("  The Eiffel   Tower! ") == "eiffel tower"


def test_exact_match():
    assert P.exact_match("The Eiffel Tower.", "eiffel tower")
    assert not P.exact_match("Eiffel", "eiffel tower")


def test_token_f1():
    assert P.token_f1("Paris, France", "Paris") == approx(2 / 3)
    assert P.token_f1("", "Paris") == 0.0
    assert P.token_f1("London", "Paris") == 0.0


def test_rouge_l():
    assert P.rouge_l("the cat sat on the mat", "the cat is on the mat") == approx(5 / 6)
    assert P.rouge_l("", "x") == 0.0


def test_best_threshold():
    scores = [0.9, 0.8, 0.6, 0.4, 0.2]
    labels = [1, 1, 0, 1, 0]
    assert P.best_threshold(scores, labels, [0.3, 0.5, 0.7, 0.85]) == 0.3


def test_pass_at_k():
    assert P.pass_at_k(10, 3, 1) == approx(0.3)
    assert P.pass_at_k(5, 4, 2) == 1.0
    assert P.pass_at_k(10, 0, 5) == 0.0
