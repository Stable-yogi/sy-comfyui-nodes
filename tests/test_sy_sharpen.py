import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_sharpen as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def near(a, b, eps=1e-6):
    return abs(a - b) < eps


def run():
    n = 0
    assert near(m.unsharp_value(0.5, 0.4, 1.0), 0.6); n += 1
    assert m.unsharp_value(0.9, 0.1, 5.0) == 1.0; n += 1
    assert m.unsharp_value(0.1, 0.9, 5.0) == 0.0; n += 1
    assert m.unsharp_value(0.5, 0.4, 0.0) == 0.5; n += 1
    flat = [0.5] * 9
    assert all(near(a, 0.5) for a in m.sharpen_line(flat, 1.0, 2.0)); n += 1
    edge = [0.2] * 6 + [0.8] * 6
    out = m.sharpen_line(edge, 1.0, 1.0)
    assert out[5] < 0.2 and out[6] > 0.8; n += 1
    assert near(out[0], 0.2); n += 1
    assert raises(m.sharpen_line, [0.1], -1, 1); n += 1
    assert raises(m.sharpen_line, [0.1], 1, -1); n += 1
    return n
