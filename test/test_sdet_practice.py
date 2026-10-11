import itertools

from common.target import load

P = load("sdet", "practice")


def test_pairwise():
    params = {"browser": ["chrome", "firefox", "safari"], "os": ["win", "mac", "linux"],
              "lang": ["en", "de", "hi"], "user": ["guest", "admin", "pro"]}
    tests = P.pairwise(params)
    assert len(tests) < 81 / 5
    for a, b in itertools.combinations(params, 2):
        covered = {(t[a], t[b]) for t in tests}
        assert covered == set(itertools.product(params[a], params[b]))
    assert P.pairwise({"x": [1, 2]}) == [{"x": 1}, {"x": 2}]


def test_heal_locator():
    old = {"id": "buy-btn", "text": "Buy now", "role": "button", "class": "btn primary"}
    candidates = [
        {"id": "", "text": "Buy now", "role": "link"},
        {"id": "", "text": "Buy now", "role": "button", "class": "btn primary"},
        {"id": "cart", "text": "Cart", "role": "button"},
    ]
    assert P.heal_locator(old, candidates) == 1
    assert P.heal_locator(old, [{"text": "Nope"}]) == -1


def test_prioritize():
    tests = {
        "test_login": {"covers": ["auth.py", "ui.py"], "recent_failures": 0},
        "test_cart": {"covers": ["cart.py"], "recent_failures": 3},
        "test_profile": {"covers": ["profile.py"], "recent_failures": 0},
        "test_logout": {"covers": ["auth.py"], "recent_failures": 1},
    }
    assert P.prioritize(tests, {"auth.py", "ui.py"}) == ["test_login", "test_cart", "test_logout"]


def test_parse_gherkin():
    text = """Feature: Login
      Scenario: Valid user
        Given I am on the login page
        When I sign in as "tom"
        Then I see the dashboard
      # comment
      Scenario: Locked user
        Given user "ana" is locked
        When I sign in as "ana"
        Then I see "Account locked"
        And no session cookie is set"""
    g = P.parse_gherkin(text)
    assert g["feature"] == "Login"
    assert [s["name"] for s in g["scenarios"]] == ["Valid user", "Locked user"]
    assert g["scenarios"][1]["steps"][-1] == "And no session cookie is set"
    assert len(g["scenarios"][0]["steps"]) == 3


def test_generate_test_data():
    schema = {"age": {"type": "int", "min": 18, "max": 65}, "plan": {"type": "choice", "values": ["free", "pro"]},
              "email": {"type": "email"}}
    rows = P.generate_test_data(schema, 3, seed=7)
    assert rows == P.generate_test_data(schema, 3, seed=7)
    assert [r["email"] for r in rows] == ["user1@example.com", "user2@example.com", "user3@example.com"]
    assert all(18 <= r["age"] <= 65 and r["plan"] in ("free", "pro") for r in rows)
    assert list(rows[0]) == ["age", "plan", "email"]


def test_triage(fake_claude):
    client = fake_claude(["Looks like DNS. <category>environment</category>", "<category>cosmic_rays</category>"])
    assert P.triage(client, "test_pay", "getaddrinfo ENOTFOUND api.local") == "environment"
    assert "<log>getaddrinfo ENOTFOUND api.local</log>" in client.last_prompt()
    assert P.triage(client, "test_pay", "???") == "needs_human"


def test_review_generated_tests():
    cases = [
        {"ID": "TC1", "Title": "Valid login", "Steps": "Sign in", "Expected": "Dashboard shown"},
        {"ID": "TC2", "Title": "valid login", "Steps": "Sign in again", "Expected": "Works"},
        {"ID": "TC3", "Title": "Logout", "Steps": "", "Expected": "Login page shown"},
    ]
    assert P.review_generated_tests(cases) == ["TC2: duplicate title", "TC2: vague expected", "TC3: missing Steps"]
