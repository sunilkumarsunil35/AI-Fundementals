from pytest import approx

from common.target import load

P = load("ml_basics", "practice")


def test_z_score():
    assert P.z_score([1, 2, 3]) == approx([-1.2247, 0.0, 1.2247], abs=1e-4)
    assert P.z_score([5, 5]) == [0.0, 0.0]


def test_one_hot():
    assert P.one_hot(["cat", "dog", "cat", "bird"]) == (
        ["bird", "cat", "dog"], [[0, 1, 0], [0, 0, 1], [0, 1, 0], [1, 0, 0]])


def test_mse_loss():
    assert P.mse_loss([1, 2, 3], [1, 2, 5]) == approx(4 / 3)


def test_knn_predict():
    pts = [[0, 0], [0, 1], [5, 5], [6, 5], [5, 6]]
    labels = ["pass", "pass", "fail", "fail", "fail"]
    assert P.knn_predict(pts, labels, [0.2, 0.3], 3) == "pass"
    assert P.knn_predict(pts, labels, [5, 5.2], 3) == "fail"
    # k=2 tie: one vote each, the nearest point wins
    assert P.knn_predict(pts, labels, [2.6, 2.6], 2) == "pass"


def test_gradient_descent_step():
    w, b = P.gradient_descent_step(0.0, 0.0, [1, 2], [2, 4], 0.1)
    assert (w, b) == approx((1.0, 0.6))
    for _ in range(500):
        w, b = P.gradient_descent_step(w, b, [1, 2, 3], [2, 4, 6], 0.05)
    assert (w, b) == approx((2.0, 0.0), abs=1e-2)


def test_logistic_predict():
    p, cls = P.logistic_predict([1.0], 0.0, [0.0])
    assert p == approx(0.5) and cls == 1
    p, cls = P.logistic_predict([2.0, -1.0], -1.0, [0.0, 1.0])
    assert p == approx(0.1192, abs=1e-4) and cls == 0


def test_k_fold_indices():
    folds = P.k_fold_indices(5, 2)
    assert folds == [([3, 4], [0, 1, 2]), ([0, 1, 2], [3, 4])]
    assert sorted(i for _, test in P.k_fold_indices(10, 3) for i in test) == list(range(10))
