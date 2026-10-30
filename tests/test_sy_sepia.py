import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_sepia as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def near(a, b, eps=1e-9):
    return abs(a - b) < eps


def run():
    n = 0
    assert m.sepia_pixel(0.2, 0.5, 0.9, 0) == (0.2, 0.5, 0.9); n += 1
    p = m.sepia_pixel(0.2, 0.2, 0.2, 1.0)
    assert near(p[0], 0.2 * 1.351) and near(p[1], 0.2 * 1.203) and near(p[2], 0.2 * 0.937); n += 1
    p = m.sepia_pixel(1.0, 1.0, 1.0, 1.0)
    assert p[0] == 1.0 and p[1] == 1.0 and near(p[2], 0.937); n += 1  # red and green clamp at 1
    assert m.sepia_pixel(0.0, 0.0, 0.0, 1.0) == (0.0, 0.0, 0.0); n += 1
    p = m.sepia_pixel(0.2, 0.2, 0.2, 0.5)
    assert near(p[0], 0.2 + (0.2 * 1.351 - 0.2) * 0.5); n += 1
    p = m.sepia_pixel(0.3, 0.6, 0.1, 1.0)
    assert p[0] > p[1] > p[2]; n += 1  # warm tone: red over green over blue
    for px in ((1, 1, 1), (0, 1, 0), (0.9, 0.9, 0.1)):
        assert all(0.0 <= v <= 1.0 for v in m.sepia_pixel(*px, 1.0)); n += 1
    p = m.sepia_pixel(0.4, 0.4, 0.4, 0.0)
    assert p == (0.4, 0.4, 0.4); n += 1
    p = m.sepia_pixel(0.3, 0.5, 0.7, 1.0)
    assert near(p[0], 0.393 * 0.3 + 0.769 * 0.5 + 0.189 * 0.7); n += 1
    msg = raises(m.sepia_pixel, 0.1, 0.1, 0.1, 1.5)
    assert msg and "strength" in msg; n += 1
    assert raises(m.sepia_pixel, 0.1, 0.1, 0.1, -0.5); n += 1
    assert len(m.MATRIX) == 3 and all(len(r) == 3 for r in m.MATRIX); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYSepia"] == "Sepia SY"; n += 1
    assert m.SYSepia.CATEGORY == "SY/Image"; n += 1
    return n
