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
    eq(m.SYTextBetween().run(t, "<a>", "</a>", "last", False, True), ("two",))
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
    eq(m.SYTextBetween.RETURN_TYPES, ("STRING",))
    return n
