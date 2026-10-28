import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_find_replace as m


def _raises(*args):
    try:
        m.find_replace(*args)
    except ValueError:
        return True
    return False


def run():
    assert m.find_replace("a b a", "a", "x") == ("x b x", 2)
    assert m.find_replace("A a", "a", "x") == ("A x", 1)
    assert m.find_replace("A a", "a", "x", False, False) == ("x x", 2)
    assert m.find_replace("a.b", ".", "-") == ("a-b", 1)  # plain mode: dot is literal
    assert m.find_replace("a.b", ".", "-", True) == ("---", 3)  # regex mode: dot matches any
    assert m.find_replace("x1 y22", r"\d+", "N", True) == ("xN yN", 2)
    assert m.find_replace("ab", r"(a)(b)", r"\2\1", True) == ("ba", 1)
    assert m.find_replace("a\\b", "\\", "/") == ("a/b", 1)
    assert m.find_replace("abc", "", "x") == ("abc", 0)
    assert m.find_replace("abc", "z", "x") == ("abc", 0)
    assert m.find_replace(None, "a", "b") == ("", 0)
    assert _raises("abc", "(", "x", True)
    assert _raises("abc", "a", r"\9", True)
    assert _raises("abc", "a" * 501, "x", True)
    assert _raises("a" * 1000001, "a", "b")
    assert m.find_replace("a" * 1000000, "a", "b")[1] == 1000000
    assert m.find_replace("a" * 500, "a" * 500, "") == ("", 1)
    assert m.find_replace("a$1", "a", "$1") == ("$1$1", 1)  # plain mode keeps replacement literal
    assert m.SYFindReplace().run("aa", "a", "b") == ("bb", 2)
    return 19  # checks
