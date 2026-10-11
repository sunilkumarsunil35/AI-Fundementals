from collections import Counter

from pytest import approx

from common.target import load

P = load("embeddings", "practice")


def test_euclidean_distance():
    assert P.euclidean_distance([0, 0], [3, 4]) == approx(5.0)


def test_mean_pool():
    assert P.mean_pool([[1, 2], [3, 4], [5, 6]]) == approx([3.0, 4.0])


def test_vector_store():
    store = P.VectorStore()
    store.add("login", [1, 0, 0], {"area": "auth"})
    store.add("logout", [0.9, 0.1, 0], {"area": "auth"})
    store.add("cart", [0, 1, 0], {"area": "shop"})
    assert len(store) == 3
    hits = store.search([1, 0, 0], 2)
    assert [h[0] for h in hits] == ["login", "logout"] and hits[0][1] == approx(1.0)
    assert [h[0] for h in store.search([1, 0, 0], 5, where={"area": "shop"})] == ["cart"]
    assert store.delete("login") and not store.delete("login")
    assert len(store) == 2


def test_mmr():
    cands = {"a": [1, 0], "a2": [0.99, 0.01], "b": [0.7, 0.7]}
    assert P.mmr([1, 0.2], cands, 2, 1.0) == ["a2", "a"]
    assert P.mmr([1, 0.2], cands, 2, 0.5) == ["a2", "b"]


def test_group_similar():
    vecs = {"t1": [1, 0], "t2": [0.95, 0.05], "t3": [0, 1], "t4": [0.1, 1]}
    assert P.group_similar(vecs, 0.9) == [["t1", "t2"], ["t3", "t4"]]


def _embed(text):
    vocab = ["login", "button", "broken", "cart", "total", "wrong"]
    c = Counter(text.lower().split())
    return [c[w] for w in vocab]


def test_find_duplicates():
    texts = {"BUG-1": "login button broken", "BUG-2": "broken login button", "BUG-3": "cart total wrong"}
    assert P.find_duplicates(texts, _embed, 0.9) == [("BUG-1", "BUG-2")]
