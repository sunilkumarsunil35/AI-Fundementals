from pytest import approx

from common.target import load

P = load("embeddings", "problems")


def test_dot():
    assert P.dot([1, 2, 3], [4, 5, 6]) == 32


def test_norm():
    assert P.norm([3, 4]) == approx(5.0)


def test_cosine_similarity():
    assert P.cosine_similarity([1, 0], [1, 0]) == approx(1.0)
    assert P.cosine_similarity([1, 0], [0, 1]) == approx(0.0)
    assert P.cosine_similarity([1, 1], [-1, -1]) == approx(-1.0)
    assert P.cosine_similarity([0, 0], [1, 1]) == 0.0


def test_normalize():
    assert P.normalize([3, 4]) == approx([0.6, 0.8])
    assert P.normalize([0, 0]) == [0.0, 0.0]


def test_top_k_similar():
    vecs = {"b": [1, 0], "a": [1, 0], "c": [0, 1], "d": [1, 1]}
    assert P.top_k_similar([1, 0.1], vecs, 3) == ["a", "b", "d"]
