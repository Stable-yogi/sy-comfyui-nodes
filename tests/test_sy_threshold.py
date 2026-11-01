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
    _k = [0]
    def _c(cond, msg="d3 check failed"):
        _k[0] += 1
        if not cond:
            raise AssertionError(msg)
    def _r(fn, *a):
        _k[0] += 1
        try:
            fn(*a)
        except ValueError as e:
            return str(e)
        raise AssertionError("expected ValueError for %r" % (a,))
    _i = m.threshold_info(0.5, 0.0, False, 25, 100)
    _c("Cut the brightness at 0.50" in _i and "25.0% of the picture is white" in _i and "soft" not in _i and "swapped" not in _i)
    _c("soft ramp of +/-0.10" in m.threshold_info(0.5, 0.1, False, 25, 100) and "swapped" in m.threshold_info(0.5, 0.0, True, 25, 100))
    _c("all black" in m.threshold_info(0.9, 0.0, False, 0, 100) and "all white" in m.threshold_info(0.1, 0.0, False, 100, 100))
    _c("Cut the red" in m.threshold_info(0.5, 0.0, False, 1, 100, "red"))
    _r(m.threshold_info, 0.5, 0.0, False, 1, 100, "alpha")
    _r(m.threshold_info, 1.5, 0.0, False, 1, 100)
    _c(m.CHANNELS[0] == "brightness" and len(m.CHANNELS) == 5)
    _c(m.SYThreshold.RETURN_NAMES == ("image", "mask", "info") and "channel" in m.SYThreshold.INPUT_TYPES()["optional"])
    return (n) + _k[0]
