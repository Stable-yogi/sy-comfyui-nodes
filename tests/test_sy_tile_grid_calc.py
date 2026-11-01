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


def _raises_run(*args):
    try:
        m.SYTileGridCalc().run(*args)
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
    # --- value pass A2: tile corners, notes, tile limit
    assert m.tile_starts(2048, 1024, 64) == [0, 960, 1024]; n += 1
    assert m.tile_starts(100, 1024, 64) == [0] and m.tile_starts(2048, 1024, 0) == [0, 1024]; n += 2
    assert m.tile_positions(2048, 1024, 1024, 0) == "0,0" + chr(10) + "1024,0"; n += 1
    assert m.tile_positions(1000, 1000, 1000, 0) == "0,0"; n += 1
    assert "too many to list" in m.tile_positions(100000, 100000, 1024, 0); n += 1
    for length in range(1, 400, 13):  # every tile stays inside the picture and the tiles reach the far edge
        st = m.tile_starts(length, 100, 10)
        assert all(0 <= s and (s + 100 <= length or len(st) == 1) for s in st) and (st[-1] + 100 >= length)
        n += 1
    assert any("last column" in t and "shares 960 pixels" in t and "instead of 64" in t for t in m.tile_notes(2048, 2048, 1024, 64)); n += 1
    assert m.tile_notes(1000, 1000, 1024, 64) == ["The picture fits in one tile, so no tiling is needed."]; n += 1
    assert m.tile_notes(1900, 1900, 1000, 100) == ["Looks fine."]; n += 1
    assert any("No overlap" in t for t in m.tile_notes(2000, 2000, 1000, 0)); n += 1
    assert any("very small" in t for t in m.tile_notes(2000, 2000, 1000, 4)); n += 1
    assert any("more than half" in t for t in m.tile_notes(2000, 2000, 1000, 600)); n += 1
    assert any("multiple of 8" in t for t in m.tile_notes(2000, 2000, 1001, 64)); n += 1
    assert any("long time" in t for t in m.tile_notes(8000, 8000, 512, 64)); n += 1
    assert any("last row" in t and "instead of 64" in t for t in m.tile_notes(1024, 2048, 1024, 64)); n += 1
    out = m.SYTileGridCalc().run(2048, 2048, 1024, 64)
    assert len(out) == len(m.SYTileGridCalc.RETURN_TYPES) == len(m.SYTileGridCalc.RETURN_NAMES) == 7 and out[4] == 960 and out[5].split(chr(10))[2] == "1024,0"; n += 1
    assert _raises_run(2048, 2048, 1024, 64, 4) and m.SYTileGridCalc().run(2048, 2048, 1024, 64, 9)[2] == 9; n += 2
    assert not _raises_run(2048, 2048, 1024, 64, 0); n += 1
    return n
