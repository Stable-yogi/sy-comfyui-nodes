import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_grow_shrink as m


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
    d = dot(7, 7, 3, 3)
    g = m.grow_shrink(d, 1, "square")
    assert sum(map(sum, g)) == 9 and g[2][2] == 1.0 and g[4][4] == 1.0
    g = m.grow_shrink(d, 1, "round")  # plus shape
    assert sum(map(sum, g)) == 5 and g[2][2] == 0.0 and g[3][2] == 1.0
    g = m.grow_shrink(d, 2, "round")
    assert g[3][5] == 1.0 and g[5][5] == 0.0
    n += 3
    assert m.grow_shrink(d, 0) == d
    n += 1
    full = [[1.0] * 7 for _ in range(7)]
    assert m.grow_shrink(full, -2) == full  # the image border does not erode
    n += 1
    block = [[1.0 if 2 <= x <= 4 and 2 <= y <= 4 else 0.0 for x in range(7)] for y in range(7)]
    s = m.grow_shrink(block, -1, "square")
    assert sum(map(sum, s)) == 1 and s[3][3] == 1.0
    assert sum(map(sum, m.grow_shrink(block, -2, "square"))) == 0
    n += 2
    empty = [[0.0] * 4 for _ in range(4)]
    assert m.grow_shrink(empty, 3) == empty and m.grow_shrink(empty, -3) == empty
    n += 1
    assert raises(m.grow_shrink, d, 5000)
    assert raises(m.grow_shrink, d, 1, "triangle")
    n += 2
    _k = [0]
    def _c(cond, msg="d3 check failed"):
        _k[0] += 1
        if not cond:
            raise AssertionError(msg)
    def _r(fn, *a):
        _k[0] += 1
        try:
            fn(*a)
        except ValueError as e:
            return str(e)
        raise AssertionError("expected ValueError for %r" % (a,))
    _c("unchanged" in m.grow_shrink_info(0, "round", 10, 10, 100))
    _c("Grew" in m.grow_shrink_info(3, "round", 10, 30, 100) and "30.0%" in m.grow_shrink_info(3, "round", 10, 30, 100))
    _c("Shrunk" in m.grow_shrink_info(-3, "square", 30, 10, 100))
    _c("Nothing white is left" in m.grow_shrink_info(-3, "round", 30, 0, 100))
    _c("whole mask is white" in m.grow_shrink_info(3, "round", 30, 100, 100))
    _c("was empty" in m.grow_shrink_info(3, "round", 0, 0, 100))
    _c(m.SYMaskGrowShrink.RETURN_NAMES == ("mask", "info") and len(m.SYMaskGrowShrink.RETURN_TYPES) == 2)
    return (n) + _k[0]
