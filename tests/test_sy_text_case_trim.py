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
    assert m.SYTextCaseTrim().run("  a ", "upper")[0] == "A"; n += 1
    return n + _extra()


def _extra():
    n = 0
    assert m.tidy_commas_line("a ,b,, c,") == "a, b, c"; n += 1
    assert m.tidy_commas_line(", ,cat , dog ,") == "cat, dog"; n += 1
    assert m.tidy_commas_line("1,000 apples , 2,500 pears") == "1,000 apples, 2,500 pears"; n += 1
    assert m.tidy_commas_line("") == ""; n += 1
    assert m.case_trim("a ,b,,c\n\n,d ,", "keep", True, False, False, True) == "a, b, c\n\nd"; n += 1
    assert m.case_trim("a ,b", tidy_commas=False) == "a ,b"; n += 1
    assert m.case_trim("A ,B,", "lower", True, True, True, True) == "a, b"; n += 1
    assert m.case_info("a", "a") == "No change: the text was already clean"; n += 1
    assert m.case_info(" a \n\n b", "a\nb") == "Cleaned: 7 -> 3 characters, 3 -> 2 line(s)"; n += 1
    out = m.SYTextCaseTrim().run("x ,y,", "keep", True, False, False, True)
    assert out == ("x, y", "Cleaned: 5 -> 4 characters, 1 -> 1 line(s)"); n += 1
    assert m.case_trim("don't stop, it's O'Neil's", "title") == "Don't Stop, It's O'neil's"; n += 1
    assert m.case_trim("hello big-world 3d", "title") == "Hello Big-World 3D"; n += 1
    assert m.SYTextCaseTrim.RETURN_NAMES == ("text", "info"); n += 1
    return n
