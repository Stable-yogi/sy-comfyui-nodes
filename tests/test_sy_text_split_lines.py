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
    assert out == (["x", "y", "z"], "y", 3); n += 1
    assert m.SYTextSplitLines.OUTPUT_IS_LIST == (True, False, False); n += 1
    return n
