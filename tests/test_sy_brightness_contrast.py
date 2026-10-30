import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_brightness_contrast as m


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
    for v in (0.0, 0.25, 0.5, 0.8, 1.0):
        assert m.bc_value(v, 0, 0) == v; n += 1
    assert near(m.contrast_factor(0), 1.0); n += 1
    assert m.contrast_factor(50) > 1.0 and m.contrast_factor(-50) < 1.0; n += 1
    assert near(m.contrast_factor(50), math.tan(1.5 * math.pi / 4)); n += 1
    # extremes are clamped to -99..99 so the factor stays finite
    assert m.contrast_factor(100) == m.contrast_factor(99); n += 1
    assert m.contrast_factor(-100) == m.contrast_factor(-99); n += 1
    assert near(m.bc_value(0.5, 0, 80), 0.5); n += 1
    assert near(m.bc_value(0.5, 20, 0), 0.7); n += 1
    assert near(m.bc_value(0.3, -10, 0), 0.2); n += 1
    assert m.bc_value(0.9, 50, 0) == 1.0; n += 1
    assert m.bc_value(0.1, -50, 0) == 0.0; n += 1
    assert m.bc_value(0.6, 0, 50) > 0.6 and m.bc_value(0.4, 0, 50) < 0.4; n += 1
    assert m.bc_value(0.6, 0, -50) < 0.6 and m.bc_value(0.4, 0, -50) > 0.4; n += 1
    msg = raises(m.bc_value, 0.5, 120, 0)
    assert msg and "brightness" in msg; n += 1
    msg = raises(m.bc_value, 0.5, 0, -120)
    assert msg and "contrast" in msg; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYBrightnessContrast"] == "Brightness Contrast SY"; n += 1
    return n
