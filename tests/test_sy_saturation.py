import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_saturation as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def near(a, b, eps=1e-6):
    return abs(a - b) < eps


def luma(p):
    return 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]


def run():
    n = 0
    for mode in m.MODES:
        assert m.saturate_pixel(0.2, 0.5, 0.9, 0, mode) == (0.2, 0.5, 0.9); n += 1
    p = m.saturate_pixel(0.9, 0.2, 0.1, -100, "saturation")
    assert near(p[0], p[1]) and near(p[1], p[2]) and near(p[0], luma((0.9, 0.2, 0.1))); n += 1
    p = m.saturate_pixel(0.5, 0.5, 0.5, 80, "saturation")
    assert all(near(v, 0.5) for v in p); n += 1
    # grey stays grey in vibrance too
    p = m.saturate_pixel(0.3, 0.3, 0.3, -60, "vibrance")
    assert all(near(v, 0.3) for v in p); n += 1
    # saturation +50 moves red channel away from grey
    src = (0.6, 0.4, 0.4)
    g = luma(src)
    p = m.saturate_pixel(*src, 50, "saturation")
    assert near(p[0], g + (0.6 - g) * 1.5); n += 1
    # clamp
    p = m.saturate_pixel(1.0, 0.0, 0.0, 100, "saturation")
    assert all(0.0 <= v <= 1.0 for v in p) and p[0] == 1.0 and p[1] == 0.0; n += 1
    # vibrance: a dull colour moves more than a strong one
    dull = (0.55, 0.5, 0.45)
    strong = (0.9, 0.5, 0.1)
    d_dull = abs(m.saturate_pixel(*dull, 50, "vibrance")[0] - dull[0]) / abs(dull[0] - luma(dull))
    d_strong = abs(m.saturate_pixel(*strong, 50, "vibrance")[0] - strong[0]) / abs(strong[0] - luma(strong))
    assert d_dull > d_strong; n += 1
    # vibrance factor of a fully saturated pixel stays 1
    p = m.saturate_pixel(1.0, 0.0, 0.5, 70, "vibrance")
    assert near(p[0], 1.0) and near(p[1], 0.0); n += 1
    # vibrance exact formula
    src = (0.6, 0.5, 0.4)
    s = 0.2
    f = 1 + 0.5 * (1 - s)
    g = luma(src)
    p = m.saturate_pixel(*src, 50, "vibrance")
    assert near(p[0], g + (0.6 - g) * f); n += 1
    msg = raises(m.saturate_pixel, 0.1, 0.1, 0.1, 101, "saturation")
    assert msg and "amount" in msg; n += 1
    assert raises(m.saturate_pixel, 0.1, 0.1, 0.1, -101, "saturation"); n += 1
    msg = raises(m.saturate_pixel, 0.1, 0.1, 0.1, 10, "nope")
    assert msg and "mode" in msg; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYSaturation"] == "Saturation SY"; n += 1
    assert m.SYSaturation.CATEGORY == "SY/Image"; n += 1
    return n
