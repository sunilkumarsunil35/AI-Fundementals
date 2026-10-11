from pytest import approx

from common.target import load

P = load("ml_basics", "problems")


def test_mean_and_std():
    assert P.mean_and_std([2, 4, 4, 4, 5, 5, 7, 9]) == approx((5.0, 2.0))


def test_min_max_scale():
    assert P.min_max_scale([10, 20, 30]) == approx([0.0, 0.5, 1.0])
    assert P.min_max_scale([3, 3]) == [0.0, 0.0]


def test_train_test_split():
    rows = list(range(10))
    train, test = P.train_test_split(rows, 0.3, seed=42)
    assert len(test) == 3 and len(train) == 7
    assert sorted(train + test) == rows
    assert rows == list(range(10)), "don't shuffle the caller's list"
    assert P.train_test_split(rows, 0.3, seed=42) == (train, test), "same seed, same split"


def test_predict_linear():
    assert P.predict_linear([2, -1], 0.5, [3, 4]) == approx(2.5)


def test_fit_line():
    slope, intercept = P.fit_line([1, 2, 3, 4], [3, 5, 7, 9])
    assert (slope, intercept) == approx((2.0, 1.0))
