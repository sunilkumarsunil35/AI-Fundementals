from pytest import approx

from common.target import load

P = load("nlp", "problems")


def test_normalize_text():
    assert P.normalize_text("  Hello,   WORLD!! ") == "hello world"


def test_tokenize():
    assert P.tokenize("Don't panic: 42 tests FAILED.") == ["don't", "panic", "42", "tests", "failed"]


def test_ngrams():
    assert P.ngrams(["a", "b", "c"], 2) == [("a", "b"), ("b", "c")]
    assert P.ngrams(["a"], 2) == []


def test_bag_of_words():
    vocab, vectors = P.bag_of_words(["the cat", "the cat the dog"])
    assert vocab == ["cat", "dog", "the"]
    assert vectors == [[1, 0, 1], [1, 1, 2]]


def test_tf_idf():
    w = P.tf_idf(["login fails", "login works"])
    assert w[0]["login"] == approx(0.5)
    assert w[0]["fails"] == approx(0.5 * (1 + __import__("math").log(1.5)))
    assert w[0]["fails"] > w[0]["login"], "rare words weigh more"
