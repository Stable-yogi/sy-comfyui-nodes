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


def _raises_rules(rules):
    try:
        m.parse_rules(rules)
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
    assert m.SYFindReplace().run("aa", "a", "b")[:2] == ("bb", 2)
    assert m.find_replace("cat category Cat", "cat", "dog", False, False, True) == ("dog category dog", 2)
    assert m.find_replace("cat category", "cat", "dog", False, True, False) == ("dog dogegory", 2)
    assert m.find_replace("a1 b22 c", r"[a-z]\d+", "X", True, True, True) == ("X X c", 2)
    assert m.find_replace("aaa", "a", "b", False, True, False, 2) == ("bba", 2)
    assert m.find_replace("a1 b2 c3", r"\d", "#", True, True, False, 1) == ("a# b2 c3", 1)
    assert _raises("abc", "a", "b", False, True, False, -1)
    assert m.parse_rules("a => b\n\n# note\n  c=>\r\nd => e => f") == [("a", "b"), ("c", ""), ("d", "e => f")]
    assert m.parse_rules("") == [] and m.parse_rules(None) == []
    assert _raises_rules("no arrow here") and _raises_rules(" => x")
    assert m.apply_rules("a b c", "a => 1\nb => 2\n1 => one") == ("one 2 c", 3)
    assert m.apply_rules("Cat cat", "cat => dog", False) == ("dog dog", 2)
    assert m.apply_rules("cat category", "cat => dog", True, True) == ("dog category", 1)
    assert m.replace_info("a a", "a", 2) == "Replaced 2 times."
    assert m.replace_info("a", "a", 1) == "Replaced 1 time."
    assert m.replace_info("Cat", "cat", 0, True) == "No exact match, but the text is there in other capital letters: turn case_sensitive off."
    assert m.replace_info("dog", "cat", 0, True) == "No match found, the text is unchanged."
    assert m.replace_info("dog", "", 0) == "Nothing to do: find is empty."
    assert m.replace_info("dog", "", 0, True, 2) == "No match found, the text is unchanged."
    assert m.SYFindReplace().run("a b", "a", "x", rules="b => y") == ("x y", 2, "Replaced 2 times.")
    assert m.SYFindReplace().run("Cat", "cat", "x") == ("Cat", 0, "No exact match, but the text is there in other capital letters: turn case_sensitive off.")
    assert m.SYFindReplace().run("a a a", "a", "b", max_count=1)[:2] == ("b a a", 1)
    assert m.SYFindReplace.RETURN_NAMES == ("text", "count", "info")
    return 41  # checks
