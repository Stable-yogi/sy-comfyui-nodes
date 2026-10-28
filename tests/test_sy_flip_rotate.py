import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_flip_rotate as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def near(a, b, eps=1e-6):
    return abs(a - b) < eps


def run():
    n = 0
    g = [[1, 2, 3], [4, 5, 6]]
    assert m.flip_rotate_grid(g, False, False, "none") == g; n += 1
    assert m.flip_rotate_grid(g, True, False, "none") == [[3, 2, 1], [6, 5, 4]]; n += 1
    assert m.flip_rotate_grid(g, False, True, "none") == [[4, 5, 6], [1, 2, 3]]; n += 1
    assert m.flip_rotate_grid(g, False, False, "90 clockwise") == [[4, 1], [5, 2], [6, 3]]; n += 1
    assert m.flip_rotate_grid(g, False, False, "180") == [[6, 5, 4], [3, 2, 1]]; n += 1
    assert m.flip_rotate_grid(g, False, False, "270 clockwise") == [[3, 6], [2, 5], [1, 4]]; n += 1
    assert m.flip_rotate_grid(g, True, True, "180") == g; n += 1
    four = g
    for _ in range(4):
        four = m.flip_rotate_grid(four, False, False, "90 clockwise")
    assert four == g; n += 1
    assert m.turn_steps("180") == 2; n += 1
    assert raises(m.turn_steps, "45"); n += 1
    assert m.SYFlipRotate.RETURN_TYPES == ("IMAGE",); n += 1
    return n
