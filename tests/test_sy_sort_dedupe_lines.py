import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_sort_dedupe_lines as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    L = ["pear", "Apple", "apple", "", "  ", "fig", "pear"]
    assert m.process_lines(L, "none", False, True, False) == L; n += 1
    assert m.process_lines(L, "none", False, True, True) == ["pear", "Apple", "apple", "fig", "pear"]; n += 1
    assert m.process_lines(L, "none", True, True, True) == ["pear", "Apple", "fig"]; n += 1
    assert m.process_lines(L, "none", True, False, True) == ["pear", "Apple", "apple", "fig"]; n += 1
    assert m.process_lines(L, "a-z", True, True, True) == ["Apple", "fig", "pear"]; n += 1
    assert m.process_lines(L, "z-a", True, True, True) == ["pear", "fig", "Apple"]; n += 1
    assert m.process_lines(["b", "B", "a", "A"], "a-z", False, False, True) == ["A", "B", "a", "b"]; n += 1
    # stable when comparing lower-cased
    assert m.process_lines(["b", "B", "a", "A"], "a-z", False, True, True) == ["a", "A", "b", "B"]; n += 1
    assert m.process_lines(["ccc", "a", "bb"], "shortest first", False, True, True) == ["a", "bb", "ccc"]; n += 1
    assert m.process_lines(["ccc", "a", "bb"], "longest first", False, True, True) == ["ccc", "bb", "a"]; n += 1
    assert m.process_lines(["bb", "aa", "c"], "shortest first", False, True, True) == ["c", "bb", "aa"]; n += 1
    assert m.process_lines(["x\r", "y\r"], "none", False, True, True) == ["x", "y"]; n += 1
    assert m.process_lines([], "a-z", True, True, True) == []; n += 1
    assert m.process_lines([""], "none", True, True, False) == [""]; n += 1
    msg = raises(m.process_lines, ["a"], "random", True, True, True)
    assert msg and "sort" in msg; n += 1
    node = m.SYSortDedupeLines()
    assert node.run("b\nA\nb\n\nc", "a-z", True, True, True) == ("A\nb\nc", 3); n += 1
    assert node.run("", "none", True, True, True) == ("", 0); n += 1
    assert raises(node.run, 5, "none", True, True, True); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYSortDedupeLines"] == "Sort Dedupe Lines SY"; n += 1
    return n
