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
    assert m.SYXYLabelStrip.RETURN_TYPES[:1] == ("STRING",) and m.SYXYLabelStrip.RETURN_NAMES == ("table", "count", "cell_list", "info"); n += 1
    assert len(m.SYXYLabelStrip.RETURN_TYPES) == 4; n += 1
    assert m.cell_lines("a\nb", "p\nq", "S", "C") == ["1: S=a, C=p", "2: S=b, C=p", "3: S=a, C=q", "4: S=b, C=q"]; n += 1
    assert m.cell_lines("a", "", "", "") == ["1: X=a"]; n += 1
    assert m.cell_lines("", "p\nq") == ["1: Y=p", "2: Y=q"]; n += 1
    try:
        m.cell_lines("", "")
        raise SystemExit("must raise")
    except ValueError:
        n += 1
    assert m.grid_info("a\nb\nc", "p\nq") == "Grid 3 columns x 2 rows = 6 pictures."; n += 1
    assert m.grid_info("a", "") == "Grid 1 columns x 1 row = 1 pictures."; n += 1
    assert "Warning: X repeats a" in m.grid_info("a\nA\nb", ""); n += 1
    assert "Warning: Y repeats" in m.grid_info("a", "p\np"); n += 1
    assert "a lot to render" in m.grid_info("\n".join(str(i) for i in range(7)), "\n".join(str(i) for i in range(6))); n += 1
    assert "a lot" not in m.grid_info("a\nb", "p"); n += 1
    return n
