import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_prompt_cleaner as m


def _fails(fn, args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


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
    assert m.SYPromptCleaner().run("a, a") == ("a", 1, "Kept 1 tag; removed 1 repeated."); n += 1
    x = m.clean_prompt_ex
    assert f("a, (a:1.2), b") == "a, (a:1.2), b"; n += 1
    assert f("a, (a:1.2), [a], b", ignore_weights=True) == "a, b"; n += 1
    assert f("(Cat:1.3), cat", ignore_weights=True) == "(Cat:1.3)"; n += 1
    assert f("(a, b:1.2), (a,b:0.5)", ignore_weights=True) == "(a, b:1.2), (a,b:0.5)"; n += 1
    assert f("(a, b:1.2), a, b", ignore_weights=True) == "(a, b:1.2), a, b"; n += 1
    assert f("a, b, c, d", drop_tags="b, C") == "a, d"; n += 1
    assert f("a, (b:1.2), c", drop_tags="b", ignore_weights=True) == "a, c"; n += 1
    assert f("a, (b:1.2), c", drop_tags="b") == "a, (b:1.2), c"; n += 1
    assert f("A, B", lowercase=True) == "a, b"; n += 1
    assert f("A, a", case_insensitive=False, lowercase=True) == "a"; n += 1
    assert x("a,, b ,  ,c,") == ("a, b, c", 0, 3, 0); n += 1
    assert x("a, a, b, A") == ("a, b", 2, 0, 0); n += 1
    assert x("a, b, c", drop_tags="a,c") == ("b", 0, 0, 2); n += 1
    assert x("") == ("", 0, 0, 0) or x("") == ("", 0, 1, 0); n += 1
    assert m.tag_key("[ Cat  ]", True, True) == "cat"; n += 1
    assert m.tag_key("(cat:1.2)", False, True) == "cat"; n += 1
    assert m.tag_key("(cat:1.2)", True, False) == "(cat:1.2)"; n += 1
    assert m.cleaner_info(3, 0, 0, 0) == "Kept 3 tags; nothing to remove."; n += 1
    assert m.cleaner_info(1, 2, 3, 4) == "Kept 1 tag; removed 2 repeated, 3 empty, 4 dropped."; n += 1
    assert m.SYPromptCleaner().run("a, (a:1.2), ,b", True, True, "b") == ("a", 2, "Kept 1 tag; removed 1 repeated, 1 empty, 1 dropped."); n += 1
    assert m.SYPromptCleaner().run("", True)[2] == "Kept 0 tags; nothing to remove." or m.SYPromptCleaner().run("", True)[2].startswith("Kept 0 tags"); n += 1
    assert m.SYPromptCleaner.RETURN_NAMES == ("text", "removed_count", "info"); n += 1
    assert _fails(f, ("a", True, False, 5)); n += 1
    return n
