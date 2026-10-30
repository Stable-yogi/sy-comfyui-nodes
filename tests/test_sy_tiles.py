import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_tiles as m


def raises(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def coverage(info, scale):
    """Sum of weights at every output pixel; returns the smallest value."""
    w = info["width"] * scale
    h = info["height"] * scale
    acc = [[0.0] * w for _ in range(h)]
    for x0, y0, wx, wy in m.merge_plan(info, scale):
        for j, vy in enumerate(wy):
            row = acc[y0 + j]
            for i, vx in enumerate(wx):
                row[x0 + i] += vy * vx
    return min(min(r) for r in acc)


def run():
    n = 0
    # tile_starts
    assert m.tile_starts(30, 64, 8) == [0]; n += 1          # side smaller than tile
    assert m.tile_starts(64, 64, 8) == [0]; n += 1          # exactly one tile
    assert m.tile_starts(100, 64, 16) == [0, 36]; n += 1    # two tiles, last shifted back
    assert m.tile_starts(100, 40, 0) == [0, 40, 60]; n += 1 # overlap 0, last shifted back
    assert m.tile_starts(80, 40, 0) == [0, 40]; n += 1
    assert m.tile_starts(100, 40, 10) == [0, 30, 60]; n += 1
    assert raises(m.tile_starts, 100, 64, 64); n += 1       # overlap not smaller than tile
    assert raises(m.tile_starts, 100, 64, 100); n += 1
    assert raises(m.tile_starts, 0, 64, 8); n += 1
    # make_info / parse_info
    info = m.make_info(100, 70, 40, 10)
    assert info["xs"] == [0, 30, 60] and info["ys"] == [0, 30] and info["cols"] == 3 and info["rows"] == 2; n += 1
    assert info["tile_w"] == 40 and info["tile_h"] == 40; n += 1
    assert m.parse_info(json.dumps(info)) == info; n += 1
    small = m.make_info(30, 20, 64, 8)
    assert small["tile_w"] == 30 and small["tile_h"] == 20 and small["cols"] == 1 and small["rows"] == 1; n += 1
    assert m.parse_info(json.dumps(small)) == small; n += 1
    for key in m.INFO_KEYS:
        broken = dict(info)
        del broken[key]
        try:
            m.parse_info(json.dumps(broken))
            raise SystemExit("missing key must raise")
        except ValueError as e:
            assert key in str(e)
        n += 1
    assert raises(m.parse_info, "not json {"); n += 1
    assert raises(m.parse_info, "[1, 2]"); n += 1
    assert raises(m.parse_info, None); n += 1
    # ramp_1d
    assert m.ramp_1d(5, 0, 0) == [1.0] * 5; n += 1
    r = m.ramp_1d(6, 2, 0)
    assert r[0] < r[1] < 1.0 and r[2:] == [1.0] * 4; n += 1
    r = m.ramp_1d(6, 0, 2)
    assert r[-1] < r[-2] < 1.0 and r[:4] == [1.0] * 4; n += 1
    r = m.ramp_1d(8, 3, 3)
    assert r[0] == r[-1] and r[3] == 1.0 and r[4] == 1.0; n += 1
    for args in ((10, 0, 0), (10, 4, 0), (10, 0, 4), (10, 4, 4), (6, 5, 5), (1, 3, 3)):
        vals = m.ramp_1d(*args)
        assert len(vals) == args[0] and all(0.0 < v <= 1.0 for v in vals); n += 1
    assert raises(m.ramp_1d, 0, 0, 0); n += 1
    assert raises(m.ramp_1d, 5, -1, 0); n += 1
    # scale_factor
    assert m.scale_factor(info, 40, 40) == 1; n += 1
    assert m.scale_factor(info, 80, 80) == 2; n += 1
    assert m.scale_factor(info, 160, 160) == 4; n += 1
    assert raises(m.scale_factor, info, 60, 60); n += 1       # 1.5
    assert raises(m.scale_factor, info, 80, 120); n += 1      # width and height disagree
    assert raises(m.scale_factor, info, 20, 20); n += 1       # smaller than the tile
    # merge_plan: every pixel is covered by weight
    for scale in (1, 2):
        assert coverage(info, scale) > 0.0; n += 1
    assert len(m.merge_plan(info, 1)) == 6; n += 1
    assert coverage(m.make_info(100, 70, 40, 0), 1) > 0.0; n += 1
    assert coverage(m.make_info(100, 70, 40, 39), 2) > 0.0; n += 1
    assert raises(m.merge_plan, info, 0); n += 1
    # node shape
    assert m.SYTileSplit.RETURN_TYPES == ("IMAGE", "STRING"); n += 1
    assert m.SYTileMerge.RETURN_TYPES == ("IMAGE",); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYTileSplit"] == "Tile Split SY"; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYTileMerge"] == "Tile Merge SY"; n += 1
    return n
