import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_motion_blur as m


def _refuses(fn, word):
    try:
        fn()
    except ValueError as e:
        assert word in str(e), str(e)
        return 1
    raise SystemExit("expected ValueError")


def run():
    n = 0
    # normal: weights add to 1 for every shape
    for shape in m.SHAPES:
        taps = m.blur_taps(30, 0.0, 16, shape)
        assert len(taps) == 16 and abs(sum(t[2] for t in taps) - 1.0) < 1e-12
        n += 1
    # angle 0 goes right (dx grows, dy 0); 90 goes up (dy negative)
    t0 = m.blur_taps(30, 0.0, 5, "even")
    assert t0[0][0] == 0.0 and abs(t0[-1][0] - 30.0) < 1e-9 and all(abs(t[1]) < 1e-9 for t in t0)
    t90 = m.blur_taps(30, 90.0, 5, "even")
    assert abs(t90[-1][1] + 30.0) < 1e-9 and all(abs(t[0]) < 1e-9 for t in t90)
    n += 2
    # centred is balanced around the pixel
    tc = m.blur_taps(20, 0.0, 9, "centred")
    assert abs(sum(t[0] * t[2] for t in tc)) < 1e-9 and abs(tc[0][0] + 10.0) < 1e-9
    n += 1
    # fade out: weights fall one by one
    tf = m.blur_taps(20, 0.0, 8, "fade out")
    assert all(tf[i][2] > tf[i + 1][2] for i in range(7))
    n += 1
    # edge: length 1 is one tap that does nothing; 360 degrees equals 0
    assert m.blur_taps(1, 45.0, 16, "even") == [(0.0, 0.0, 1.0)]
    a, b = m.blur_taps(10, 360.0, 3, "even"), m.blur_taps(10, 0.0, 3, "even")
    assert all(abs(p[0] - q[0]) < 1e-9 and abs(p[1] - q[1]) < 1e-9 for p, q in zip(a, b))
    assert len(m.blur_taps(400, 0.0, 64, "even")) == 64 and len(m.blur_taps(400, 0.0, 3, "even")) == 3
    n += 3
    # refusals
    n += _refuses(lambda: m.blur_taps(0, 0.0, 16, "even"), "length")
    n += _refuses(lambda: m.blur_taps(401, 0.0, 16, "even"), "length")
    n += _refuses(lambda: m.blur_taps(10, 400.0, 16, "even"), "angle")
    n += _refuses(lambda: m.blur_taps(10, 0.0, 2, "even"), "samples")
    n += _refuses(lambda: m.blur_taps(10, 0.0, 16, "wavy"), "shape")
    n += _refuses(lambda: m.blur_tensor(None, 10, 0.0, "wavy", 16), "shape")
    d = m.SYMotionBlur.INPUT_TYPES()["required"]
    assert d["length"][1]["default"] == 30 and d["samples"][1]["default"] == 16 and d["shape"][1]["default"] == "even"
    n += 1
    assert math.isfinite(sum(t[2] for t in tf))
    n += 1
    return n
