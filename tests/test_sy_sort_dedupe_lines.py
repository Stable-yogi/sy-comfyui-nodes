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
    assert node.run("b\nA\nb\n\nc", "a-z", True, True, True)[:2] == ("A\nb\nc", 3); n += 1
    assert node.run("", "none", True, True, True)[:2] == ("", 0); n += 1
    assert raises(node.run, 5, "none", True, True, True); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYSortDedupeLines"] == "Sort Dedupe Lines SY"; n += 1
    return n + _extra()


def _extra():
    n = 0
    assert m.process_lines(["cat", "cat ", " cat"], "none", True, True, True) == ["cat", "cat ", " cat"]; n += 1
    assert m.process_lines(["cat", "cat ", " cat"], "none", True, True, True, True) == ["cat"]; n += 1
    assert m.process_lines(["  ", "a "], "none", False, True, False, True) == ["", "a"]; n += 1
    out, st = m.process_lines_report(["a", "A", "", "b", "a "], "none", True, True, True)
    assert out == ["a", "b", "a "] and st == {"input": 5, "empty": 1, "duplicates": 1, "padded": 1}; n += 1
    assert m.lines_info(st, 3) == "Kept 3 of 5 line(s); removed 1 repeated and 1 empty; 1 line(s) have spaces at the ends, so 'cat ' and 'cat' count as different (turn on trim_lines)"; n += 1
    assert m.lines_info(st, 3, True).endswith("1 empty"); n += 1
    assert m.lines_info({"input": 2, "empty": 0, "duplicates": 0, "padded": 0}, 2) == "Kept 2 of 2 line(s)"; n += 1
    r = m.SYSortDedupeLines().run("cat\ncat \nb", "none", True, True, True, True)
    assert r[:2] == ("cat\nb", 2) and r[2].startswith("Kept 2 of 3") and "1 repeated" in r[2]; n += 1
    assert m.SYSortDedupeLines.RETURN_NAMES[-1] == "info"; n += 1
    return n
