import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_solarize as m


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
    assert m.solarize_value(1.0, 1.0) == 0.0; n += 1
    assert m.solarize_value(0.99, 1.0) == 0.99; n += 1
    assert m.solarize_value(0.0, 1.0) == 0.0; n += 1
    assert near(m.solarize_value(0.8, 0.5), 0.2); n += 1
    assert m.solarize_value(0.5, 0.5) == 0.5; n += 1  # 1 - 0.5 is 0.5
    assert m.solarize_value(0.4, 0.5) == 0.4; n += 1
    assert m.solarize_value(0.0, 0.0) == 1.0; n += 1
    assert m.solarize_value(1.0, 0.0) == 0.0; n += 1
    assert near(m.solarize_value(0.6, 0.6), 0.4); n += 1
    for v in (0.0, 0.2, 0.7, 1.0):  # never leaves 0..1
        assert 0.0 <= m.solarize_value(v, 0.3) <= 1.0; n += 1
    msg = raises(m.solarize_value, 0.5, 1.5)
    assert msg and "threshold" in msg; n += 1
    assert raises(m.solarize_value, 0.5, -0.1); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYSolarize"] == "Solarize SY"; n += 1
    assert m.SYSolarize.CATEGORY == "SY/Image"; n += 1
    return n
