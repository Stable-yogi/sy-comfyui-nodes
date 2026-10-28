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
    return n
