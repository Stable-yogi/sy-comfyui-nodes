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
    assert m.SYRegexExtract().run("n=7", r"n=(\d)", 1)[:2] == ("7", True); n += 1
    return n + _extra()


def _extra():
    n = 0
    f = m.regex_extract_full
    assert f("a1 b22 c333", r"(\d+)", 1, "", False, True) == ("1, 22, 333", True, "Found 3 match(es) of group 1, joined with ', '"); n += 1
    assert f("a1 b22", r"(\d+)", 1, "", False, True, "|")[0] == "1|22"; n += 1
    assert f("abc", r"(\d+)", 1, "none", False, True)[:2] == ("none", False); n += 1
    assert m.regex_extract("a1 b2", r"\d", 0, "", False, True, "") == ("12", True); n += 1
    r = f("seed 1234 end", r"(\d+)", 1)
    assert r[:2] == ("1234", True) and "position 5" in r[2] and "4 character" in r[2]; n += 1
    r = f("ABC", "abc", 0)
    assert r[:2] == ("", False) and "WOULD match if ignore_case" in r[2] and "(empty)" in r[2]; n += 1
    assert "WOULD" not in f("xyz", "abc", 0, "d")[2] and "'d'" in f("xyz", "abc", 0, "d")[2]; n += 1
    assert f("ABC", "abc", 0, "", True)[1] is True; n += 1
    assert raises(lambda: f("x", "(a)", 2, "", False, True)); n += 1
    out = m.SYRegexExtract().run("a1 b2", r"(\d)", 1, "", False, True, "+")
    assert out[0] == "1+2" and out[1] is True and len(out) == 3; n += 1
    assert m.SYRegexExtract.RETURN_NAMES == ("result", "matched", "info"); n += 1
    return n
