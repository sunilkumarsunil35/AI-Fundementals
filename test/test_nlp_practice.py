from common.target import load

P = load("nlp", "practice")


def test_estimate_tokens():
    assert P.estimate_tokens("") == 0
    assert P.estimate_tokens("abcde") == 2


def test_sentence_split():
    assert P.sentence_split("It failed. Why? Network!  Retry ok.") == ["It failed.", "Why?", "Network!", "Retry ok."]


def test_remove_stopwords():
    assert P.remove_stopwords(["The", "test", "is", "red"], {"the", "is"}) == ["test", "red"]


def test_jaccard():
    assert P.jaccard("login page broken", "Login page slow") == 0.5
    assert P.jaccard("", "") == 1.0


def test_edit_distance():
    assert P.edit_distance("kitten", "sitting") == 3
    assert P.edit_distance("", "abc") == 3


def test_chunk_words():
    text = "a b c d e f g"
    assert P.chunk_words(text, 3, 1) == ["a b c", "c d e", "e f g"]
    assert P.chunk_words("a b", 5, 2) == ["a b"]


def test_bpe_merges():
    merges = P.bpe_merges(["low", "lower", "lowest", "low"], 3)
    assert merges == [("l", "o"), ("lo", "w"), ("low", "e")]
    assert P.bpe_merges(["a"], 2) == []
