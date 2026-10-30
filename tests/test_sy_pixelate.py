import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_pixelate as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def near(a, b, eps=1e-9):
    return abs(a - b) < eps


def run():
    n = 0
    assert m.block_ranges(10, 4) == [(0, 4), (4, 8), (8, 10)]; n += 1
    assert m.block_ranges(8, 4) == [(0, 4), (4, 8)]; n += 1
    assert m.block_ranges(3, 8) == [(0, 3)]; n += 1
    assert m.block_ranges(1, 1) == [(0, 1)]; n += 1
    assert m.block_ranges(5, 1) == [(i, i + 1) for i in range(5)]; n += 1
    assert raises(m.block_ranges, 0, 4); n += 1
    assert raises(m.block_ranges, 4, 0); n += 1
    g = [[float(x + 10 * y) for x in range(5)] for y in range(3)]
    assert m.pixelate_grid(g, 1, "average") == g; n += 1
    assert m.pixelate_grid(g, 1, "nearest") == g; n += 1
    nr = m.pixelate_grid(g, 2, "nearest")
    assert nr[0][0] == nr[0][1] == nr[1][0] == nr[1][1] == 0.0; n += 1
    assert nr[0][4] == nr[1][4] == 4.0 and nr[2][0] == nr[2][1] == 20.0; n += 1
    av = m.pixelate_grid(g, 2, "average")
    assert near(av[0][0], (0 + 1 + 10 + 11) / 4.0) and av[1][1] == av[0][0]; n += 1
    assert near(av[2][4], 24.0) and near(av[2][2], (22 + 23) / 2.0); n += 1  # smaller edge blocks use their own pixels only
    big = m.pixelate_grid(g, 100, "average")
    assert all(near(v, sum(sum(r) for r in g) / 15.0) for row in big for v in row); n += 1
    assert m.pixelate_grid([[7.0]], 8, "nearest") == [[7.0]]; n += 1
    assert m.pixelate_grid([[1.0, 3.0, 5.0, 7.0]], 4, "average") == [[4.0] * 4]; n += 1
    assert raises(m.pixelate_grid, g, 2, "bilinear"); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYPixelate"] == "Pixelate SY"; n += 1
    return n
