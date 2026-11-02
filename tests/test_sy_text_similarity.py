import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_similarity as m


def run():
    n = 0
    r = m.similarity_ratio
    assert r("", "") == 1.0; n += 1
    assert r("a b c", "a b c") == 1.0; n += 1
    assert r("a b c", "") == 0.0; n += 1
    assert r("", "x") == 0.0; n += 1
    assert r("cat", "dog", "words") == 0.0; n += 1
    assert abs(r("a b c d", "a b c e") - 0.75) < 1e-9; n += 1
    assert r("Hello", "hello", "characters", True) == 1.0; n += 1
    assert r("Hello", "hello", "characters", False) < 1.0; n += 1
    assert 0.0 < r("abcd", "abxd", "characters") < 1.0; n += 1
    assert r("  a   b ", "a b") == 1.0; n += 1   # extra spaces do not matter for words
    for args, word in ((("a", "b", "sentences"), "compare_by"), ((None, "b"), "both texts")):
        try:
            r(*args)
            raise SystemExit("bad input must raise")
        except ValueError as e:
            assert word in str(e)
            n += 1
    node = m.SYTextSimilarity()
    assert node.run("a b", "a b") == (1.0, True); n += 1
    assert node.run("a b", "c d", threshold=0.5) == (0.0, False); n += 1
    assert node.run("a b c d", "a b c e", threshold=0.75)[1] is True; n += 1
    return n
