import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_strip_markdown as m


def run():
    n = 0
    s = m.strip_markdown
    assert s("# Title\n\nSome **bold** and *italic* and __bold2__ and _it2_.") == "Title\n\nSome bold and italic and bold2 and it2."; n += 1
    assert s("- one\n* two\n+ three") == "one\ntwo\nthree"; n += 1
    assert s("- one\n* two", keep_bullets=True) == "- one\n- two"; n += 1
    assert s("See [the docs](http://x.y/z) now") == "See the docs now"; n += 1
    assert s("See [the docs](http://x.y/z) now", keep_link_text=False) == "See  now"; n += 1
    assert s("![a cat](c.png) here") == "a cat here"; n += 1
    assert s("use `a*b*c` ok") == "use a*b*c ok"; n += 1   # code content untouched
    assert s("```python\nx = 1 * 2 * 3\n```\nend") == "x = 1 * 2 * 3\nend"; n += 1
    assert s("a\n\n\n\n\nb") == "a\n\nb"; n += 1
    assert s("## Head ##") == "Head"; n += 1
    assert s("> quote\n---\n~~gone~~") == "quote\n\ngone"; n += 1
    assert s("snake_case_name stays and 2 * 3 stays") == "snake_case_name stays and 2 * 3 stays"; n += 1
    assert s("***both***") == "both"; n += 1
    assert s("") == ""; n += 1
    assert s("1. first\n2. second") == "1. first\n2. second"; n += 1
    try:
        s(None)
        raise SystemExit("non text must raise")
    except ValueError as e:
        assert "must be text" in str(e)
        n += 1
    assert m.SYStripMarkdown().run("**x**") == ("x",); n += 1
    return n
