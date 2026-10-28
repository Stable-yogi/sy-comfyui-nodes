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
    eq(node.run("a, b", "b, c"), ("a", "c", "b", 1, 1, 1))
    eq(node.run("x, y", "x, y"), ("", "", "x, y", 0, 0, 2))
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
    eq(len(m.SYPromptDiff.RETURN_TYPES), 6)
    return n
