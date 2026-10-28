import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_invert_threshold as m


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
    a = [[0.0, 0.3, 0.5, 1.0]]
    assert m.invert_threshold(a, False, False, 0.5) == a
    assert m.invert_threshold(a, True, False, 0.5) == [[1.0, 0.7, 0.5, 0.0]]
    assert m.invert_threshold(a, False, True, 0.5) == [[0.0, 0.0, 1.0, 1.0]]
    assert m.invert_threshold(a, True, True, 0.5) == [[1.0, 1.0, 0.0, 0.0]]
    n += 4
    assert m.invert_threshold(a, False, True, 0.0) == [[1.0, 1.0, 1.0, 1.0]]
    assert m.invert_threshold(a, False, True, 1.0) == [[0.0, 0.0, 0.0, 1.0]]
    n += 2
    assert raises(m.invert_threshold, a, True, True, 1.5)
    n += 1
    return n
