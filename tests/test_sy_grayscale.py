import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_grayscale as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def near(a, b, eps=1e-6):
    return abs(a - b) < eps


def run():
    n = 0
    assert near(m.grey_value(1, 0, 0, "rec709"), 0.2126); n += 1
    assert near(m.grey_value(0, 1, 0, "rec709"), 0.7152); n += 1
    assert near(m.grey_value(0, 0, 1, "rec709"), 0.0722); n += 1
    assert near(m.grey_value(1, 0, 0, "rec601"), 0.299); n += 1
    assert near(m.grey_value(0, 1, 0, "rec601"), 0.587); n += 1
    assert near(m.grey_value(0, 0, 1, "rec601"), 0.114); n += 1
    assert near(m.grey_value(0.3, 0.6, 0.9, "average"), 0.6); n += 1
    assert near(m.grey_value(0.2, 0.6, 0.8, "lightness"), 0.5); n += 1
    for meth in m.METHODS:
        assert near(m.grey_value(0.5, 0.5, 0.5, meth), 0.5); n += 1
        assert near(m.grey_value(1, 1, 1, meth), 1.0); n += 1
    assert raises(m.grey_value, 0, 0, 0, "nope"); n += 1
    msg = raises(m.grayscale_pixel, (0, 0, 0), "rec709", 1.5)
    assert msg and "strength" in msg; n += 1
    assert raises(m.grayscale_pixel, (0, 0, 0), "rec709", -0.1); n += 1
    assert m.grayscale_pixel((0.2, 0.4, 0.6), "rec709", 0.0) == (0.2, 0.4, 0.6); n += 1
    p = m.grayscale_pixel((1.0, 0.0, 0.0), "rec709", 1.0)
    assert near(p[0], p[1]) and near(p[1], p[2]) and near(p[0], 0.2126); n += 1
    h = m.grayscale_pixel((1.0, 0.0, 0.0), "average", 0.5)
    assert near(h[0], 1.0 - 0.5 * (1.0 - 1.0 / 3.0)) and near(h[1], 1.0 / 6.0); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYGrayscale"] == "Grayscale SY"; n += 1
    return n
