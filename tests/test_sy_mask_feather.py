import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_feather as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def dot(h, w, x, y, v=1.0):
    r = [[0.0] * w for _ in range(h)]
    r[y][x] = v
    return r


def run():
    n = 0
    d = dot(9, 9, 4, 4)
    assert m.feather(d, 0) == d
    f = m.feather(d, 2)
    assert abs(sum(map(sum, f)) - 1.0) < 1e-9  # mass kept
    assert f[4][4] < 1.0 and f[4][4] > f[4][2] > 0.0
    n += 3
    full = [[1.0] * 6 for _ in range(6)]
    assert all(abs(v - 1.0) < 1e-9 for r in m.feather(full, 3) for v in r)  # solid stays solid
    n += 1
    edge = [[1.0 if x < 3 else 0.0 for x in range(8)] for _ in range(3)]
    fe = m.feather(edge, 2)
    assert fe[1][0] > 0.99 and fe[1][7] < 0.01 and 0.0 < fe[1][3] < 1.0
    n += 1
    assert raises(m.feather, d, -1) and raises(m.feather, d, 9999)
    n += 1
    # --- grow first, edge modes, info
    one = [[0.0] * 9 + [1.0] + [0.0] * 9]
    assert m.feather(one, 0, "centred", 0) == one
    g = m.feather(one, 0, "centred", 2)
    assert g[0][7] == 1.0 and g[0][11] == 1.0 and g[0][6] == 0.0 and g[0][12] == 0.0
    n += 2
    blk = [[1.0 if 6 <= x <= 12 else 0.0 for x in range(19)] for _ in range(5)]
    inside = m.feather(blk, 3, "inside only")
    outside = m.feather(blk, 3, "outside only")
    centred = m.feather(blk, 3)
    assert all(inside[2][x] <= blk[2][x] + 1e-9 for x in range(19))  # no halo outside the subject
    assert all(outside[2][x] >= blk[2][x] - 1e-9 for x in range(19))  # never smaller
    assert centred[2][4] > 0.0 and inside[2][4] == 0.0 and outside[2][4] > 0.0
    assert inside[2][6] < 1.0 and outside[2][6] == 1.0
    n += 4
    assert raises(m.feather, blk, 2, "sideways") and raises(m.feather, blk, 2, "centred", 9999)
    n += 1
    t = m.feather_info(0, "centred", 0, 100, 100, 12.0, 12.0)
    assert "left as it is" in t and "12.0% selected" in t
    t = m.feather_info(5, "inside only", 3, 100, 100, 10.0, 9.0)
    assert "grown 3 px, then feathered 5 px (inside only)" in t and "in this order" in t
    t = m.feather_info(5, "centred", 0, 100, 100, 0.0, 0.0)
    assert "empty" in t.lower() and "nothing to feather" in t
    t = m.feather_info(60, "centred", -2, 100, 100, 10.0, 8.0)
    assert "shrunk 2 px" in t and "more than half the picture" in t
    n += 4
    return n
