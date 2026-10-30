import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_ease_curve as m


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
    samples = [i / 10.0 for i in range(11)]
    for c in m.CURVES:
        assert near(m.ease(0.0, c), 0.0); n += 1
        assert near(m.ease(1.0, c), 1.0); n += 1
        vals = [m.ease(t, c) for t in samples]
        assert all(vals[i] <= vals[i + 1] + 1e-12 for i in range(10)); n += 1
    for c in ("linear", "ease_in_out_quad", "ease_in_out_cubic", "smoothstep", "smootherstep"):
        assert near(m.ease(0.5, c), 0.5); n += 1
    assert near(m.ease(0.5, "ease_in_quad"), 0.25); n += 1
    assert near(m.ease(0.5, "ease_out_quad"), 0.75); n += 1
    assert near(m.ease(0.5, "ease_in_cubic"), 0.125); n += 1
    assert near(m.ease(0.5, "ease_out_cubic"), 0.875); n += 1
    assert near(m.ease(0.25, "ease_in_out_quad"), 0.125); n += 1
    assert near(m.ease(0.75, "ease_in_out_cubic"), 1 - (0.5) ** 3 / 2); n += 1
    assert near(m.ease(0.25, "smoothstep"), 3 * 0.0625 - 2 * 0.015625); n += 1
    assert near(m.ease(0.25, "smootherstep"), 6 * 0.25 ** 5 - 15 * 0.25 ** 4 + 10 * 0.25 ** 3); n += 1
    v, e = m.ease_value(0.5, "linear", 10.0, 20.0)
    assert near(v, 15.0) and near(e, 0.5); n += 1
    v, e = m.ease_value(1.0, "smoothstep", -5.0, 5.0)
    assert near(v, 5.0); n += 1
    v, e = m.ease_value(0.0, "smoothstep", 7.0, 3.0)
    assert near(v, 7.0); n += 1
    v, e = m.ease_value(0.5, "ease_in_quad", 2.0, 2.0)
    assert near(v, 2.0) and near(e, 0.25); n += 1
    msg = raises(m.ease, 0.5, "bounce")
    assert msg and "curve" in msg; n += 1
    msg = raises(m.ease, 1.5, "linear")
    assert msg and "t" in msg; n += 1
    assert raises(m.ease, -0.1, "linear"); n += 1
    assert m.SYEaseCurve().run(0.5, "linear", 0.0, 10.0) == (5.0, 0.5); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYEaseCurve"] == "Ease Curve SY"; n += 1
    return n
