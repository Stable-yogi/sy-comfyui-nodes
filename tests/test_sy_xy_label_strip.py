import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_xy_label_strip as m


def run():
    n = 0
    t = m.make_table("a\nb", "p\nq", "Sampler", "CFG")
    lines = t.split("\n")
    assert lines[0] == "| CFG \\ Sampler | a | b |"; n += 1
    assert lines[1] == "|---|---|---|"; n += 1
    assert lines[2] == "| p | 0 | 1 |" and lines[3] == "| q | 2 | 3 |"; n += 1
    t = m.make_table("a|b", "", "", " ")
    assert t.split("\n")[0] == "| Y \\ X | a\\|b |" and t.split("\n")[2] == "|  | 0 |"; n += 1
    assert m.make_table("", "p\nq", "X", "Y").split("\n")[2:] == ["| p | 0 |", "| q | 1 |"]; n += 1
    try:
        m.make_table("", "", "X", "Y")
        raise SystemExit("must raise")
    except ValueError:
        n += 1
    assert m.SYXYLabelStrip.RETURN_TYPES == ("STRING",); n += 1
    return n
