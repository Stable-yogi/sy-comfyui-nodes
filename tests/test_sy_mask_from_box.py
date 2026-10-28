import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_from_box as m


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
    k = m.box_mask(1, 1, 2, 2, 4, 4)
    assert k == [[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]]
    n += 1
    k = m.box_mask(2, 2, 10, 10, 4, 4)  # box beyond the canvas is cut
    assert sum(map(sum, k)) == 4 and k[3][3] == 1
    k = m.box_mask(-2, -2, 4, 4, 4, 4)  # starts outside the canvas
    assert sum(map(sum, k)) == 4 and k[0][0] == 1 and k[2][2] == 0
    n += 2
    assert sum(map(sum, m.box_mask(10, 10, 3, 3, 4, 4))) == 0  # fully outside: empty
    assert sum(map(sum, m.box_mask(1, 1, 0, 3, 4, 4))) == 0  # zero width: empty
    n += 2
    assert raises(m.box_mask, 0, 0, -1, 2, 4, 4) and raises(m.box_mask, 0, 0, 2, 2, 0, 4)
    n += 1
    return n
