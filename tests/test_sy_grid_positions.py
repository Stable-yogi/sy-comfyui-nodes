import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_grid_positions as m


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected ValueError")


def run():
    n = 0
    # hand-computed 2x2: cells 100x50, gap 10, margin 5 -> width 5+100+10+100+5 = 220, height 5+50+10+50+5 = 120
    cells, tw, th = m.grid_cells(2, 2, 100, 50, 10, 5)
    assert cells == [(0, 5, 5, 100, 50), (1, 115, 5, 100, 50), (2, 5, 65, 100, 50), (3, 115, 65, 100, 50)]; n += 1
    assert (tw, th) == (220, 120); n += 1
    cells, tw, th = m.grid_cells(2, 2, 100, 50, 10, 5, "column by column")
    assert cells == [(0, 5, 5, 100, 50), (1, 5, 65, 100, 50), (2, 115, 5, 100, 50), (3, 115, 65, 100, 50)]; n += 1
    # 3 columns x 2 rows, row by row: index 4 is column 1, row 1
    cells, tw, th = m.grid_cells(3, 2, 10, 10, 2, 0)
    assert cells[4] == (4, 12, 12, 10, 10) and (tw, th) == (34, 22); n += 1
    # edge: single cell, no gap, no margin
    assert m.grid_cells(1, 1, 7, 9, 0, 0) == ([(0, 0, 0, 7, 9)], 7, 9); n += 1
    assert m.grid_cells(1, 1, 7, 9, 99, 3) == ([(0, 3, 3, 7, 9)], 13, 15); n += 1
    # edge: biggest
    cells, tw, th = m.grid_cells(64, 64, 16384, 16384, 1024, 4096)
    assert len(cells) == 4096 and tw == 8192 + 64 * 16384 + 63 * 1024; n += 1
    assert cells[-1][0] == 4095 and cells[-1][1] == 4096 + 63 * (16384 + 1024); n += 1
    assert m.cells_to_text([(0, 5, 5, 100, 50), (1, 115, 5, 100, 50)]) == "0,5,5,100,50\n1,115,5,100,50"; n += 1
    # refusals
    assert "at least 1" in _raises(m.grid_cells, 0, 2, 10, 10); n += 1
    assert "cell_width" in _raises(m.grid_cells, 2, 2, 0, 10); n += 1
    assert "0 or more" in _raises(m.grid_cells, 2, 2, 10, 10, -1, 0); n += 1
    assert "order must be" in _raises(m.grid_cells, 2, 2, 10, 10, 0, 0, "zigzag"); n += 1
    node = m.SYGridPositions()
    out = node.run(2, 2, 100, 50, 10, 5, "row by row")
    assert out == ("0,5,5,100,50\n1,115,5,100,50\n2,5,65,100,50\n3,115,65,100,50", 220, 120, 4); n += 1
    return n
