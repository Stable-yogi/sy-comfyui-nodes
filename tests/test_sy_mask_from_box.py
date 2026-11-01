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
    # --- anchor, invert, feather
    assert m.top_left(5, 5, 4, 2) == (5, 5) and m.top_left(5, 5, 4, 2, "centre") == (3, 4)
    k = m.box_mask(2, 2, 2, 2, 4, 4, "centre")
    assert k[1][1] == 1 and k[2][2] == 1 and sum(map(sum, k)) == 4
    n += 2
    k = m.box_mask(1, 1, 2, 2, 4, 4, invert=True)
    assert k[1][1] == 0 and k[0][0] == 1 and sum(map(sum, k)) == 12
    n += 1
    k = m.box_mask(4, 4, 3, 3, 11, 11, feather=2)
    assert 0.0 < k[2][2] < 1.0 or 0.0 < k[3][3] < 1.0
    assert abs(sum(map(sum, k)) - 9.0) < 1e-6  # feather keeps the total
    n += 2
    assert raises(m.box_mask, 0, 0, 2, 2, 4, 4, "sideways") and raises(m.box_mask, 0, 0, 2, 2, 4, 4, "centre", False, -1)
    n += 1
    # --- box report
    assert "inside the canvas" in m.box_report(1, 1, 2, 2, 4, 4)
    t = m.box_report(-2, 1, 4, 2, 8, 8)
    assert "cut off at the left" in t and "2x2" in t
    assert "cut off at the right and bottom" in m.box_report(6, 6, 4, 4, 8, 8)
    assert "completely outside" in m.box_report(20, 20, 3, 3, 8, 8) and "8x8" in m.box_report(20, 20, 3, 3, 8, 8)
    assert "no width or height" in m.box_report(1, 1, 0, 3, 8, 8)
    assert raises(m.box_report, 0, 0, -1, 2, 4, 4)
    n += 6
    return n
