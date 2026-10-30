import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_threshold as m


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
    assert m.threshold_value(0.5, 0.5, 0.0) == 1.0; n += 1
    assert m.threshold_value(0.4999, 0.5, 0.0) == 0.0; n += 1
    assert m.threshold_value(1.0, 0.5, 0.0) == 1.0; n += 1
    assert m.threshold_value(0.0, 0.5, 0.0) == 0.0; n += 1
    assert near(m.threshold_value(0.5, 0.5, 0.2), 0.5); n += 1
    assert near(m.threshold_value(0.3, 0.5, 0.2), 0.0); n += 1
    assert near(m.threshold_value(0.7, 0.5, 0.2), 1.0); n += 1
    assert near(m.threshold_value(0.6, 0.5, 0.2), 0.75); n += 1
    assert m.threshold_value(0.0, 0.5, 0.2) == 0.0; n += 1
    assert m.threshold_value(1.0, 0.5, 0.2) == 1.0; n += 1
    assert m.threshold_value(0.0, 0.0, 0.0) == 1.0; n += 1
    assert m.threshold_value(0.9, 1.0, 0.0) == 0.0; n += 1
    msg = raises(m.threshold_value, 0.5, 1.5, 0.0)
    assert msg and "level" in msg; n += 1
    msg = raises(m.threshold_value, 0.5, 0.5, 0.9)
    assert msg and "softness" in msg; n += 1
    assert raises(m.threshold_value, 0.5, -0.1, 0.0); n += 1
    assert raises(m.threshold_value, 0.5, 0.5, -0.1); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYThreshold"] == "Threshold SY"; n += 1
    return n
