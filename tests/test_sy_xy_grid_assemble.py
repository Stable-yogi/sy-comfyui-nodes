import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_xy_grid_assemble as m


def run():
    n = 0
    m.check_count(6, 3, 2); n += 1
    for args in ((5, 3, 2), (7, 3, 2), (0, 1, 1)):
        try:
            m.check_count(*args)
            raise SystemExit("must raise")
        except ValueError:
            n += 1
    assert m.SYXYGridAssemble.RETURN_TYPES == ("IMAGE", "STRING") and m.SYXYGridAssemble.RETURN_NAMES == ("grid", "info"); n += 1
    assert set(m.SYXYGridAssemble.INPUT_TYPES()["optional"]) == {"mismatch"}; n += 1
    assert m.reconcile_count(6, 3, 2) == (6, 0, ""); n += 1
    for args in ((5, 3, 2), (7, 3, 2), (5, 3, 2, "error")):
        try:
            m.reconcile_count(*args)
            raise SystemExit("must raise")
        except ValueError:
            n += 1
    fill = "fill blanks or trim"
    assert m.reconcile_count(4, 3, 2, fill)[:2] == (4, 2) and "2 empty cells" in m.reconcile_count(4, 3, 2, fill)[2]; n += 1
    assert "1 empty cell " in m.reconcile_count(5, 3, 2, fill)[2]; n += 1
    assert m.reconcile_count(8, 3, 2, fill)[:2] == (6, 0) and "last 2 were left out" in m.reconcile_count(8, 3, 2, fill)[2]; n += 1
    assert m.reconcile_count(6, 3, 2, fill) == (6, 0, ""); n += 1
    try:
        m.reconcile_count(6, 3, 2, "sideways")
        raise SystemExit("must raise")
    except ValueError:
        n += 1
    assert m.grid_info_text(6, 3, 2, 512, 512, 1600, 1100) == "Grid 3 x 2 (6 pictures, cells 512x512) -> one picture 1600x1100."; n += 1
    assert "Note: x." in m.grid_info_text(1, 1, 1, 8, 8, 8, 8, "x"); n += 1
    assert "very big picture" in m.grid_info_text(64, 8, 8, 2048, 2048, 17000, 17000); n += 1
    return n
