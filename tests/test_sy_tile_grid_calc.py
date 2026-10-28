import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_tile_grid_calc as m


def _raises(*args):
    try:
        m.tile_grid(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.tile_grid(1024, 1024, 1024, 0)[:3] == (1, 1, 1); n += 1
    assert m.tile_grid(2048, 2048, 1024, 0)[:3] == (2, 2, 4); n += 1
    assert m.tile_grid(2048, 2048, 1024, 64)[:3] == (3, 3, 9); n += 1  # overlap needs an extra tile
    assert m.tile_grid(2000, 1000, 1024, 64)[:3] == (3, 1, 3); n += 1
    assert m.tile_grid(100, 100, 1024, 64)[:3] == (1, 1, 1); n += 1  # picture smaller than a tile
    assert m.tile_grid(1, 1, 1, 0)[:3] == (1, 1, 1); n += 1
    assert m.tile_grid(5, 1, 1, 0)[:3] == (5, 1, 5); n += 1
    assert m.tile_grid(1025, 1024, 1024, 0)[:3] == (2, 1, 2); n += 1  # non-multiple
    assert m.tile_grid(1_000_000, 1_000_000, 1024, 0)[2] == 977 * 977; n += 1  # huge
    cols, rows, count, text = m.tile_grid(2048, 2048, 1024, 64)
    assert "3 columns x 3 rows = 9 tiles" in text; n += 1
    for length in range(1, 300, 7):  # tiles really cover the picture
        c = m.tile_grid(length, 1, 100, 10)[0]
        assert c == 1 or (c - 1) * 90 + 100 >= length > (c - 2) * 90 + 100
        n += 1
    for bad in ((0, 5, 4, 0), (5, 0, 4, 0), (5, 5, 0, 0), (5, 5, 4, -1), (5, 5, 4, 4), (5, 5, 4, 9), (2_000_000, 5, 4, 0)):
        assert _raises(*bad), bad
        n += 1
    assert m.SYTileGridCalc().run(2048, 2048, 1024, 0)[2] == 4; n += 1
    return n
