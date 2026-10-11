from common.target import load

P = load("sdet", "problems")

LLM_TABLE = """Here are your cases:

| ID | Title | Steps | Expected |
|----|-------|-------|----------|
| TC1 | Valid login | Enter valid user | Dashboard shown |
| TC2 | Wrong password | Enter bad password | Error shown |

Let me know if you need more."""


def test_boundary_values():
    assert P.boundary_values(1, 100) == [0, 1, 2, 99, 100, 101]
    assert P.boundary_values(5, 6) == [4, 5, 6, 7]


def test_test_case_prompt():
    p = P.test_case_prompt("Password must be 8-64 chars", 5)
    assert "<requirement>Password must be 8-64 chars</requirement>" in p
    assert "5 test cases" in p and "| ID | Title | Steps | Expected |" in p
    assert all(w in p for w in ["positive", "negative", "boundary"])


def test_parse_test_cases():
    cases = P.parse_test_cases(LLM_TABLE)
    assert cases == [
        {"ID": "TC1", "Title": "Valid login", "Steps": "Enter valid user", "Expected": "Dashboard shown"},
        {"ID": "TC2", "Title": "Wrong password", "Steps": "Enter bad password", "Expected": "Error shown"},
    ]
    assert P.parse_test_cases("no table") == []


def test_flaky_tests():
    history = {
        "test_login": ["pass", "fail", "pass", "pass"],
        "test_cart": ["pass", "pass", "fail", "fail"],
        "test_search": ["pass"] * 4,
        "test_pay": ["fail", "pass", "fail", "pass"],
    }
    assert P.flaky_tests(history) == ["test_login", "test_pay"]


def test_failure_signature():
    a = P.failure_signature("Timeout 30000ms waiting for 'button#buy' at 0x7f3a")
    b = P.failure_signature("Timeout  5000ms waiting for 'a.link' at 0x1b2c")
    assert a == b == "Timeout <N>ms waiting for <S> at <ID>"


def test_group_failures():
    fails = {
        "t_b": "Timeout 30000ms waiting for 'x'",
        "t_a": "Timeout 1000ms waiting for 'y'",
        "t_c": "AssertionError: expected 3 got 4",
    }
    assert P.group_failures(fails) == {
        "Timeout <N>ms waiting for <S>": ["t_a", "t_b"],
        "AssertionError: expected <N> got <N>": ["t_c"],
    }
