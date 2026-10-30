import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_auto_contrast as m


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
    vals = [i / 99.0 for i in range(100)]
    lo, hi = m.stretch_range(vals, 0)
    assert lo == 0.0 and hi == 1.0; n += 1
    lo, hi = m.stretch_range(vals, 10)
    assert near(lo, 9 / 99.0) and near(hi, 90 / 99.0); n += 1
    assert m.stretch_range([0.4], 5) == (0.4, 0.4); n += 1
    assert m.stretch_range([0.2, 0.8], 20) == (0.2, 0.8); n += 1
    assert m.clip_indexes(100, 1.0) == (0, 99); n += 1
    assert m.clip_indexes(1001, 1.0) == (10, 990); n += 1
    assert m.stretch_value(0.2, 0.2, 0.6) == 0.0; n += 1
    assert m.stretch_value(0.6, 0.2, 0.6) == 1.0; n += 1
    assert near(m.stretch_value(0.4, 0.2, 0.6), 0.5); n += 1
    assert m.stretch_value(0.0, 0.2, 0.6) == 0.0 and m.stretch_value(1.0, 0.2, 0.6) == 1.0; n += 1  # clamp
    assert m.stretch_value(0.7, 0.5, 0.5) == 0.7; n += 1  # flat range: unchanged
    assert m.stretch_value(0.7, 0.5, 0.5 + 1e-8) == 0.7; n += 1
    msg = raises(m.stretch_range, vals, 25)
    assert msg and "clip_percent" in msg; n += 1
    assert raises(m.stretch_range, vals, -1); n += 1
    assert raises(m.stretch_range, [], 1); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYAutoContrast"] == "Auto Contrast SY"; n += 1
    assert m.SYAutoContrast.CATEGORY == "SY/Image"; n += 1
    return n
