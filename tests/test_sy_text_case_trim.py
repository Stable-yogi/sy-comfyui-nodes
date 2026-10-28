import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_case_trim as m


def run():
    n = 0
    f = m.case_trim
    assert f("  Hello World  ") == "Hello World"; n += 1
    assert f("  Hello  ", trim=False) == "  Hello  "; n += 1
    assert f("abc", "upper") == "ABC"; n += 1
    assert f("ABC", "lower") == "abc"; n += 1
    assert f("hello big world", "title") == "Hello Big World"; n += 1
    assert f("HELLO there. how ARE you? fine", "sentence") == "Hello there. How are you? Fine"; n += 1
    assert f("a    b \t c", collapse_spaces=True) == "a b c"; n += 1
    assert f("a\n\n  \nb", strip_empty_lines=True) == "a\nb"; n += 1
    assert f("a\n\nb") == "a\n\nb"; n += 1
    assert f("", "upper") == ""; n += 1
    for bad in (("x", "weird"), (5,)):
        try:
            f(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            n += 1
    assert m.SYTextCaseTrim().run("  a ", "upper") == ("A",); n += 1
    return n
