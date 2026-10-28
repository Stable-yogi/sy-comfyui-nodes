import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_from_colour as m


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
    img = [[[0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.9, 0.0]]]
    assert m.colour_mask(img, 0, 255, 0, 0) == [[1.0, 0.0, 0.0]]
    assert m.colour_mask(img, 0, 255, 0, 30) == [[1.0, 0.0, 1.0]]  # 0.9*255 = 229.5, off by 25.5
    assert m.colour_mask(img, 0, 255, 0, 255) == [[1.0, 1.0, 1.0]]
    n += 3
    img4 = [[[0.0, 1.0, 0.0, 0.5]]]  # alpha channel ignored
    assert m.colour_mask(img4, 0, 255, 0, 0) == [[1.0]]
    n += 1
    assert raises(m.colour_mask, img, 300, 0, 0, 0) and raises(m.colour_mask, img, 0, 0, 0, 999)
    n += 1
    return n
