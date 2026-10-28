import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_levels_adjust as m


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
    px = [0.2, 0.5, 0.8]
    r = m.adjust_pixel(px, 0.0, 1.0, 1.0, 1.0)
    assert all(near(a, b) for a, b in zip(r, px)); n += 1
    r = m.adjust_pixel(px, 0.1, 1.0, 1.0, 1.0)
    assert near(r[0], 0.3) and near(r[1], 0.6) and near(r[2], 0.9); n += 1
    r = m.adjust_pixel([0.25, 0.5, 0.75], 0.0, 2.0, 1.0, 1.0)
    assert near(r[0], 0.0) and near(r[1], 0.5) and near(r[2], 1.0); n += 1
    r = m.adjust_pixel([0.25, 0.5, 0.75], 0.0, 0.0, 1.0, 1.0)
    assert all(near(a, 0.5) for a in r); n += 1
    r = m.adjust_pixel([1.0, 0.0, 0.0], 0.0, 1.0, 0.0, 1.0)
    assert near(r[0], r[1]) and near(r[1], r[2]) and near(r[0], 0.2126); n += 1
    r = m.adjust_pixel([0.25, 0.25, 0.25], 0.0, 1.0, 1.0, 2.0)
    assert near(r[0], 0.5); n += 1
    r = m.adjust_pixel([0.9, 0.9, 0.9], 1.0, 3.0, 3.0, 5.0)
    assert all(0.0 <= v <= 1.0 for v in r); n += 1
    assert raises(m.adjust_pixel, px, 0, 1, 1, 0); n += 1
    assert raises(m.adjust_pixel, px, 0, -1, 1, 1); n += 1
    return n
