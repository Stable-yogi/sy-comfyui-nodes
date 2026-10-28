import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_regex_extract as m


def raises(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


def run():
    n = 0
    f = m.regex_extract
    assert f("seed 1234 end", r"(\d+)", 1) == ("1234", True); n += 1
    assert f("seed 1234 end", r"\d+", 0) == ("1234", True); n += 1
    assert f("abc", r"(\d+)", 1, "none") == ("none", False); n += 1
    assert f("ABC", "abc", 0, "", True) == ("ABC", True); n += 1
    assert f("ABC", "abc", 0, "d", False) == ("d", False); n += 1
    assert f("k=v", r"(\w)=(\w)", 2) == ("v", True); n += 1
    assert f("x", r"(a)?x", 1, "dflt") == ("dflt", False); n += 1
    assert raises(lambda: f("x", "")); n += 1
    assert raises(lambda: f("x", "a" * 201)); n += 1
    assert f("x", "a" * 200) == ("", False); n += 1
    assert raises(lambda: f("a" * 100001, "a")); n += 1
    assert f("a" * 100000, "b") == ("", False); n += 1
    assert raises(lambda: f("x", "(unclosed")); n += 1
    assert raises(lambda: f("x", "(a)", 2)); n += 1
    assert raises(lambda: f("x", "(a)", -1)); n += 1
    assert raises(lambda: f("aaaa", "(a+)+b")); n += 1
    assert raises(lambda: f(5, "a")); n += 1
    assert m.SYRegexExtract().run("n=7", r"n=(\d)", 1) == ("7", True); n += 1
    return n
