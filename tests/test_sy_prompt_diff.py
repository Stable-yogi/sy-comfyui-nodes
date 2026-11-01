import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_prompt_diff as m


def run():
    n = 0

    def eq(got, want):
        nonlocal n
        assert got == want, "got %r, wanted %r" % (got, want)
        n += 1

    eq(m.prompt_diff("a, b, c", "b, c, d"), (["a"], ["d"], ["b", "c"]))
    eq(m.prompt_diff("Red Fox, blue", "red fox, Green"), (["blue"], ["Green"], ["Red Fox"]))
    eq(m.prompt_diff("a, a, A", "b"), (["a"], ["b"], []))
    eq(m.prompt_diff("", ""), ([], [], []))
    eq(m.prompt_diff("a;b", "b;c", ";"), (["a"], ["c"], ["b"]))
    eq(m.prompt_diff(" a ,, b ", "b"), (["a"], [], ["b"]))
    eq(m.prompt_diff(None, "x"), ([], ["x"], []))
    node = m.SYPromptDiff()
    eq(node.run("a, b", "b, c"), ("a", "c", "b", 1, 1, 1, 0.333, "A has 2 tags, B has 2 tags; 1 shared (33% alike), 1 only in A, 1 only in B."))
    eq(node.run("x, y", "x, y"), ("", "", "x, y", 0, 0, 2, 1.0, "A has 2 tags, B has 2 tags; 2 shared (100% alike), 0 only in A, 0 only in B."))
    try:
        m.prompt_diff("a", "b", "")
        raise SystemExit("empty separator must raise")
    except ValueError:
        n += 1
    try:
        m.prompt_diff("x" * (m.MAX_INPUT + 1), "b")
        raise SystemExit("too long input must raise")
    except ValueError:
        n += 1
    eq(len(m.SYPromptDiff.RETURN_TYPES), 8)
    eq(m.prompt_diff("(red:1.2), blue", "red, green"), (["(red:1.2)", "blue"], ["red", "green"], []))
    eq(m.prompt_diff("(red:1.2), blue", "red, green", ",", True), (["blue"], ["green"], ["(red:1.2)"]))
    eq(m.prompt_diff("red, (Red:0.8), [red]", "x", ",", True), (["red"], ["x"], []))
    eq(m.prompt_diff("a  b, A B", "a b"), ([], [], ["a  b"]))
    eq(m.diff_summary([], [], []), (1.0, "A has 0 tags, B has 0 tags; 0 shared (100% alike), 0 only in A, 0 only in B."))
    eq(m.diff_summary(["a"], [], []), (0.0, "A has 1 tag, B has 0 tags; 0 shared (0% alike), 1 only in A, 0 only in B."))
    eq(m.diff_summary(["a"], ["b"], ["c", "d"]), (0.5, "A has 3 tags, B has 3 tags; 2 shared (50% alike), 1 only in A, 1 only in B."))
    eq(node.run("(cat:1.1), dog", "cat", ",", True)[5:7], (1, 0.5))
    eq(m.SYPromptDiff.RETURN_NAMES[-2:], ("similarity", "info"))
    return n
