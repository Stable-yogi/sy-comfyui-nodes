import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_prompt_cleaner as m


def run():
    n = 0
    f = m.clean_prompt
    assert f("a, b, a, c") == "a, b, c"; n += 1
    assert f("a,, b ,  ,c,") == "a, b, c"; n += 1
    assert f("a   b,  c") == "a b, c"; n += 1
    assert f("Cat, cat, CAT") == "Cat"; n += 1
    assert f("Cat, cat", case_insensitive=False) == "Cat, cat"; n += 1
    assert f("(a, b:1.2), (a, b:1.2), c") == "(a, b:1.2), c"; n += 1
    assert f("z, y, x, y") == "z, y, x"; n += 1
    assert f("a,\nb,\n\na") == "a, b"; n += 1
    assert f("") == ""; n += 1
    assert f(",,,") == ""; n += 1
    assert f("a), b, (c") == "a), b, (c"; n += 1
    try:
        f(5)
        raise SystemExit("bad args must raise")
    except ValueError:
        n += 1
    assert m.SYPromptCleaner().run("a, a") == ("a",); n += 1
    return n
