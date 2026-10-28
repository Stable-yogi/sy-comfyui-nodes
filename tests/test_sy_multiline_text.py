import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_multiline_text as m


def run():
    n = 0
    f = m.strip_comments
    assert f("a\n# note\nb") == "a\nb"; n += 1
    assert f("a\n   # indented note\nb") == "a\nb"; n += 1
    assert f("a # not a comment") == "a # not a comment"; n += 1
    assert f("\\# keep") == "# keep"; n += 1
    assert f("a\n\nb") == "a\n\nb"; n += 1
    assert f("a\n\nb", keep_empty_lines=False) == "a\nb"; n += 1
    assert f("# only") == ""; n += 1
    assert f("") == ""; n += 1
    assert f("a\r\n#c\r\nb") == "a\nb"; n += 1
    try:
        f(None)
        raise SystemExit("bad args must raise")
    except ValueError:
        n += 1
    assert m.SYMultilineText().run("x\n#y") == ("x",); n += 1
    return n
