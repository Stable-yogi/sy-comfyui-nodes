import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_combine as m


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
    a = [[1.0, 1.0, 0.0, 0.0]]
    b = [[1.0, 0.0, 1.0, 0.0]]
    assert m.combine(a, b, "union") == [[1.0, 1.0, 1.0, 0.0]]
    assert m.combine(a, b, "intersect") == [[1.0, 0.0, 0.0, 0.0]]
    assert m.combine(a, b, "subtract") == [[0.0, 1.0, 0.0, 0.0]]
    assert m.combine(a, b, "xor") == [[0.0, 1.0, 1.0, 0.0]]
    n += 4
    soft = m.combine([[0.25, 0.75]], [[0.5, 0.5]], "union")
    assert soft == [[0.5, 0.75]]
    n += 1
    small = [[1.0, 0.0]]  # stretched to 4 wide
    assert m.combine(a, small, "xor") == [[0.0, 0.0, 0.0, 0.0]]  # small became [1,1,0,0]
    assert len(m.combine(a, [[1.0], [0.0]], "union")) == 1
    n += 2
    assert raises(m.combine, a, b, "bogus")
    n += 1
    # --- grow / feather / invert, in that order
    one = [[0.0] * 5 + [1.0] + [0.0] * 5]
    base = m.combine(one, one, "union")
    assert m.combine(one, one, "union", grow=0, feather=0, invert=False) == base
    g = m.combine(one, one, "union", grow=1)
    assert g[0][4] == 1.0 and g[0][6] == 1.0 and g[0][2] == 0.0
    inv = m.combine(one, one, "union", invert=True)
    assert inv[0][5] == 0.0 and inv[0][0] == 1.0
    gf = m.combine(one, one, "union", grow=1, feather=1)
    assert 0.0 < gf[0][3] < 1.0 or 0.0 < gf[0][7] < 1.0  # the soft edge sits outside the grown core
    n += 4
    assert raises(m.combine, one, one, "union", 9999, 0) and raises(m.combine, one, one, "union", 0, -1)
    n += 1
    # --- info line
    t = m.combine_info("union", (8, 8), (8, 8), 1, 1, 10.0, 20.0, 25.0)
    assert "Union of A (10.0% selected)" in t and "Result: 25.0% selected" in t and t.endswith(".")
    assert "stretched" not in t
    t = m.combine_info("intersect", (8, 8), (4, 4), 1, 3, 10.0, 20.0, 0.0)
    assert "stretched to the size of A" in t and "only the first 1 of B" in t and "do not overlap" in t
    t = m.combine_info("union", (8, 8), (8, 8), 1, 1, 0.0, 0.0, 0.0)
    assert "Both input masks are empty" in t
    t = m.combine_info("subtract", (8, 8), (8, 8), 1, 1, 30.0, 40.0, 0.0)
    assert "B covers all of A" in t
    t = m.combine_info("union", (8, 8), (8, 8), 1, 1, 5.0, 5.0, 9.0, 2, 3, True)
    assert "grown 2 px, then feathered 3 px, then inverted" in t and "grow always comes before feather" in t
    n += 5
    t = m.combine_info("union", (8, 8), (8, 8), 1, 1, 5.0, 5.0, 9.0, -2)
    assert "shrunk 2 px" in t
    n += 1
    return n
