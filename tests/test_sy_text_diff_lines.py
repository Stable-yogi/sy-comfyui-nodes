import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_diff_lines as m


def run():
    n = [0]

    def eq(got, want):
        n[0] += 1
        assert got == want, "got %r want %r" % (got, want)

    eq(m.diff_lines("a\nb\nc", "b\nc\nd"), (["a"], ["d"], ["b", "c"]))
    eq(m.diff_lines("a\na\nb", "b\nb"), (["a"], [], ["b"]))
    eq(m.diff_lines("A\nb", "a\nB"), (["A", "b"], ["a", "B"], []))
    eq(m.diff_lines("A\nb", "a\nB", True), ([], [], ["A", "b"]))
    eq(m.diff_lines("  a  \nb", "a\n b"), ([], [], ["a", "b"]))
    eq(m.diff_lines("  a  \nb", "a\nb", False, False), (["  a  "], ["a"], ["b"]))
    eq(m.diff_lines("a\n\n  \nb", "\n\nb"), (["a"], [], ["b"]))
    eq(m.diff_lines("", ""), ([], [], []))
    eq(m.diff_lines("z\ny\nx", "x\ny"), (["z"], [], ["y", "x"]))
    eq(m.summary_text(["1", "2", "3"], ["4"], list("12345678")), "3 only in A, 1 only in B, 8 in both")
    node = m.SYTextDiffLines()
    eq(node.run("a\nb", "b\nc"), ("a", "c", "b", "1 only in A, 1 only in B, 1 in both"))
    eq(node.run("x", "X", True, True)[3], "0 only in A, 0 only in B, 1 in both")
    eq(m.SYTextDiffLines.RETURN_NAMES, ("only_a", "only_b", "both", "summary"))
    eq(m.NODE_DISPLAY_NAME_MAPPINGS["SYTextDiffLines"], "Text Diff Lines SY")
    return n[0]
