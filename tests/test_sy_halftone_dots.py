import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_halftone_dots as m


def refuses(fn, *args):
    try:
        fn(*args)
    except ValueError as e:
        return len(str(e)) > 10
    return False


def run():
    n = 0
    assert m.dot_radius(0.0, 8) == 0.0; n += 1
    assert abs(m.dot_radius(1.0, 10) - 7.0) < 1e-9; n += 1
    assert m.dot_radius(0.25, 8) < m.dot_radius(0.75, 8); n += 1
    assert abs(m.dot_radius(0.25, 10) - 3.5) < 1e-9; n += 1
    assert refuses(m.dot_radius, 1.5, 8); n += 1
    assert refuses(m.dot_radius, -0.1, 8); n += 1
    assert refuses(m.dot_radius, 0.5, 0); n += 1
    i, j, du, dv = m.cell_of(0, 0, 0, 8)
    assert (i, j) == (0, 0) and du == -4 and dv == -4; n += 1
    i, j, du, dv = m.cell_of(12, 4, 0, 8)
    assert (i, j) == (1, 0) and abs(du) < 1e-9 and abs(dv) < 1e-9; n += 1
    i, j, _, _ = m.cell_of(5, 5, 90, 8)
    assert (i, j) == (0, -1); n += 1
    assert m.check_settings(3, 0, 0, "keep colour") is None; n += 1
    assert m.check_settings(64, 90, 1, "black on white") is None; n += 1
    assert refuses(m.check_settings, 2, 45, 0.2, "keep colour"); n += 1
    assert refuses(m.check_settings, 65, 45, 0.2, "keep colour"); n += 1
    assert refuses(m.check_settings, 8, 91, 0.2, "keep colour"); n += 1
    assert refuses(m.check_settings, 8, 45, 1.5, "keep colour"); n += 1
    assert refuses(m.check_settings, 8, 45, 0.2, "red"); n += 1
    assert m.SYHalftoneDots.RETURN_NAMES == ("image",) and m.SYHalftoneDots.CATEGORY == "SY/Image"; n += 1
    return n
