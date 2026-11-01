import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_between as m


def run():
    n = 0

    def eq(got, want):
        nonlocal n
        assert got == want, "got %r, wanted %r" % (got, want)
        n += 1

    t = "x <a>one</a> y <a>two</a> z"
    eq(m.text_between(t, "<a>", "</a>"), "one")
    eq(m.text_between(t, "<a>", "</a>", "last"), "two")
    eq(m.text_between(t, "<a>", "</a>", "first", True), "<a>one</a>")
    eq(m.text_between(t, "<A>", "</A>", case_sensitive=False), "one")
    eq(m.text_between("a [b.c] d", "[", "]"), "b.c")
    eq(m.text_between('say "hi" and "bye"', '"', '"', "last"), "bye")
    eq(m.text_between("s\nline1\nline2\ne", "s\n", "\ne"), "line1\nline2")
    eq(m.text_between("<a>x<a>y</a>", "<a>", "</a>"), "x<a>y")
    eq(m.text_between("<a></a>", "<a>", "</a>"), "")
    eq(m.SYTextBetween().run(t, "<a>", "</a>", "last", False, True)[0], "two")
    for args in ((t, "", "</a>"), (t, "<a>", ""), (t, "<b>", "</a>"), ("<a>open", "<a>", "</a>"), (t, "<A>", "</a>"),
                 (t, "<a>", "</a>", "middle")):
        try:
            m.text_between(*args)
            raise SystemExit("bad marker must raise: %r" % (args,))
        except ValueError:
            n += 1
    try:
        m.text_between("x" * (m.MAX_INPUT + 1), "a", "b")
        raise SystemExit("too long input must raise")
    except ValueError:
        n += 1
    eq(m.SYTextBetween.RETURN_TYPES, ("STRING", "STRING"))
    return n + _extra()


def _extra():
    n = 0
    t = "Sure! ```json\n{\"a\": 1}\n``` Hope it helps"
    assert m.text_between(t, "```json", "```", "first", False, True, "stop with an error", True) == '{"a": 1}'; n += 1
    assert m.text_between(t, "```json", "```") == '\n{"a": 1}\n'; n += 1
    assert m.text_between("no fence", "```", "```", "first", False, True, "give empty text") == ""; n += 1
    assert m.text_between("no fence", "```", "```", "first", False, True, "give the whole text") == "no fence"; n += 1
    assert m.text_between("<a>open", "<a>", "</a>", "first", False, True, "give empty text") == ""; n += 1
    r, info = m.text_between_info("x <a>one</a>", "<a>", "</a>")
    assert r == "one" and info == "Found the first pair of markers; 3 character(s) at position 2", info; n += 1
    r, info = m.text_between_info("x <A>one</A>", "<a>", "</a>", if_missing="give empty text")
    assert r == "" and info.startswith("Not found, gave empty text") and "other letter case" in info; n += 1
    r, info = m.text_between_info("x", "<a>", "</a>", if_missing="give the whole text")
    assert r == "x" and "whole text" in info; n += 1
    try:
        m.text_between("x <A>", "<a>", "</a>")
        raise SystemExit("missing marker must raise")
    except ValueError as e:
        assert "letter case" in str(e); n += 1
    try:
        m.text_between("x", "a", "b", if_missing="whatever")
        raise SystemExit("bad if_missing must raise")
    except ValueError:
        n += 1
    out = m.SYTextBetween().run("[ hi ]", "[", "]", "first", False, True, "stop with an error", True)
    assert out[0] == "hi" and out[1].startswith("Found"); n += 1
    assert m.SYTextBetween.RETURN_NAMES == ("text", "info"); n += 1
    return n
