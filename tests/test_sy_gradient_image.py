import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_gradient_image as m
import _sy_hexcolour as hx


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
    assert near(m.gradient_t(0, 0, 4, 1, "linear", 0), 0.125); n += 1
    assert near(m.gradient_t(3, 0, 4, 1, "linear", 0), 0.875); n += 1
    assert near(m.gradient_t(0, 0, 1, 4, "linear", 90), 0.125); n += 1
    assert near(m.gradient_t(0, 3, 1, 4, "linear", 90), 0.875); n += 1
    assert near(m.gradient_t(3, 0, 4, 1, "linear", 180), 0.125); n += 1
    assert near(m.gradient_t(0, 3, 1, 4, "linear", 270), 0.125); n += 1
    assert near(m.gradient_t(0, 0, 4, 1, "linear", -360), 0.125); n += 1
    assert near(m.gradient_t(0, 0, 1, 1, "linear", 33), 0.5); n += 1
    assert near(m.gradient_t(0, 0, 1, 1, "radial", 0), 0.0); n += 1
    assert m.gradient_t(0, 0, 100, 100, "linear", 45) < 0.01; n += 1
    assert m.gradient_t(99, 99, 100, 100, "linear", 45) > 0.99; n += 1
    assert m.gradient_t(49, 49, 100, 100, "radial", 0) < 0.02; n += 1
    assert m.gradient_t(0, 0, 100, 100, "radial", 0) > 0.98; n += 1
    assert 0.0 <= m.gradient_t(0, 0, 5, 3, "radial", 0) <= 1.0; n += 1
    assert m.gradient_pixel(0.0, (0, 0, 0), (1, 1, 1)) == (0, 0, 0); n += 1
    assert m.gradient_pixel(0.5, (0, 0, 0), (1, 1, 1)) == (0.5, 0.5, 0.5); n += 1
    assert raises(m.gradient_t, 0, 0, 0, 5, "linear", 0); n += 1
    assert raises(m.gradient_t, 0, 0, 5, 5, "conical", 0); n += 1
    assert hx.parse_hex(m.DEFAULT_A) == hx.parse_hex("1b1b2f") and m.DEFAULT_B == "#f5d58a"; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYGradientImage"] == "Gradient Image SY"; n += 1
    return n
