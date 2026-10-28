import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_to_box as m


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


def blockmask(w, h, x0, y0, x1, y1):
    return [[1.0 if x0 <= x <= x1 and y0 <= y <= y1 else 0.0 for x in range(w)] for y in range(h)]


def run():
    n = 0
    k = blockmask(10, 8, 3, 2, 5, 4)
    assert m.mask_to_box(k, 0, 0.5, "error") == (3, 2, 3, 3)
    assert m.mask_to_box(k, 1, 0.5, "error") == (2, 1, 5, 5)
    n += 2
    assert m.mask_to_box(k, 100, 0.5, "error") == (0, 0, 10, 8)  # padding clamped to the image
    edge = blockmask(10, 8, 0, 0, 1, 1)
    assert m.mask_to_box(edge, 3, 0.5, "error") == (0, 0, 5, 5)
    n += 2
    assert m.mask_to_box(blockmask(10, 8, 9, 7, 9, 7), 2, 0.5, "error") == (7, 5, 3, 3)
    n += 1
    empty = blockmask(10, 8, 5, 5, 4, 4)
    assert m.mask_to_box(empty, 4, 0.5, "whole_image") == (0, 0, 10, 8)
    assert raises(m.mask_to_box, empty, 0, 0.5, "error")
    n += 2
    soft = [[0.2, 0.9]]
    assert m.mask_to_box(soft, 0, 0.5, "error") == (1, 0, 1, 1)
    assert m.mask_to_box(soft, 0, 0.1, "error") == (0, 0, 2, 1)
    n += 2
    assert raises(m.mask_to_box, k, -1, 0.5, "error") and raises(m.mask_to_box, k, 0, 0.5, "bogus")
    n += 1
    return n
