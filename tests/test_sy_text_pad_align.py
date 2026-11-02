import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_pad_align as m


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected ValueError")


def run():
    n = 0
    assert m.pad_lines(["a", "abc"]) == (["a  ", "abc"], 3); n += 1
    assert m.pad_lines(["a", "abc"], "right") == (["  a", "abc"], 3); n += 1
    assert m.pad_lines(["a", "abcd"], "centre") == ([" a  ", "abcd"], 4); n += 1   # extra space on the right
    assert m.pad_lines(["ab"], "centre", 5, "-") == (["-ab--"], 5); n += 1
    assert m.pad_lines(["ab"], "left", 4, ".") == (["ab.."], 4); n += 1
    # edge: width bigger than all, long lines kept or cut
    assert m.pad_lines(["abcdef"], "left", 3) == (["abcdef"], 6); n += 1
    assert m.pad_lines(["abcdef", "x"], "left", 3, " ", True) == (["abc", "x  "], 3); n += 1
    # edge: empty and single, biggest width
    assert m.pad_lines([]) == ([], 0); n += 1
    assert m.pad_lines([""]) == ([""], 0); n += 1
    assert m.pad_lines([""], "right", 500, "*")[0][0] == "*" * 500; n += 1
    # characters, not bytes
    assert m.pad_lines(["éé", "abcd"], "right") == (["  éé", "abcd"], 4); n += 1
    # refusals
    assert "exactly one character" in _raises(m.pad_lines, ["a"], "left", 0, "ab"); n += 1
    assert "exactly one character" in _raises(m.pad_lines, ["a"], "left", 0, ""); n += 1
    assert "exactly one character" in _raises(m.pad_lines, ["a"], "left", 0, "\n"); n += 1
    assert "align must be" in _raises(m.pad_lines, ["a"], "middle"); n += 1
    assert "width must be" in _raises(m.pad_lines, ["a"], "left", -1); n += 1
    node = m.SYTextPadAlign()
    assert node.run("a\nabc\n", "right", 0, " ", False) == ("  a\nabc", 3); n += 1
    assert node.run("", "left", 0, " ", False) == ("", 0); n += 1
    assert node.run("a\r\nbb", "left", 3, "_", False) == ("a__\nbb_", 3); n += 1
    return n
