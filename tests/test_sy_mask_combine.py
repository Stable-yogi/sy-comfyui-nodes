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
    return n
