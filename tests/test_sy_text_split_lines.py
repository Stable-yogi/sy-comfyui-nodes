import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_split_lines as m


def run():
    n = 0
    assert m.split_lines("a\n\nb\n  \nc") == ["a", "b", "c"]; n += 1
    assert m.split_lines("a\n\nb", skip_empty=False) == ["a", "", "b"]; n += 1
    assert m.split_lines("") == []; n += 1
    L = ["a", "b", "c"]
    assert m.pick_line(L, 0) == "a"; n += 1
    assert m.pick_line(L, 2) == "c"; n += 1
    assert m.pick_line(L, 4) == "b"; n += 1
    assert m.pick_line(L, -1) == "c"; n += 1
    for call in (lambda: m.pick_line([], 0), lambda: m.split_lines(3)):
        try:
            call()
            raise SystemExit("bad args must raise")
        except ValueError:
            n += 1
    out = m.SYTextSplitLines().run("x\ny\nz", 4, True)
    assert out[:3] == (["x", "y", "z"], "y", 3); n += 1
    assert m.SYTextSplitLines.OUTPUT_IS_LIST == (True, False, False, False); n += 1
    return n + _extra()


def _extra():
    n = 0
    t = " a \n# note\n\n  b\n   # indented note\nc"
    assert m.split_lines(t, True, True, True) == ["a", "b", "c"]; n += 1
    assert m.split_lines(t, True, False, True) == [" a ", "  b", "c"]; n += 1
    assert m.split_lines(t, True, True, False) == ["a", "# note", "b", "# indented note", "c"]; n += 1
    assert m.split_lines(t, False, True, True) == ["a", "", "b", "c"]; n += 1
    assert m.split_lines("  x  ", True, True) == ["x"]; n += 1
    assert m.lines_info(3, 1) == "3 line(s); picked line 2 (index 1)"; n += 1
    assert m.lines_info(3, 4) == "3 line(s); picked line 2 (index 1), index 4 wrapped around"; n += 1
    assert m.lines_info(3, -1).startswith("3 line(s); picked line 3"); n += 1
    out = m.SYTextSplitLines().run("# c\n a \nb", 5, True, True, True)
    assert out[0] == ["a", "b"] and out[1] == "b" and out[2] == 2 and "wrapped around" in out[3]; n += 1
    assert m.SYTextSplitLines.RETURN_NAMES[-1] == "info"; n += 1
    return n
