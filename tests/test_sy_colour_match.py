import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_colour_match as m


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
    assert m.mean_std([0.0, 1.0]) == (0.5, 0.5); n += 1
    assert near(m.mean_std([0.3] * 4)[1], 0.0); n += 1
    out = m.match_values([0.2, 0.4, 0.6], 0.5, 0.1, 1.0)
    mean, std = m.mean_std(out)
    assert near(mean, 0.5) and near(std, 0.1); n += 1
    src = [0.2, 0.4, 0.6]
    assert m.match_values(src, 0.9, 0.3, 0.0) == src; n += 1
    half = m.match_values([0.2, 0.4, 0.6], 0.5, 0.1, 0.5)
    full = m.match_values([0.2, 0.4, 0.6], 0.5, 0.1, 1.0)
    assert near(half[0], (0.2 + full[0]) / 2.0); n += 1
    flat = m.match_values([0.5, 0.5], 0.8, 0.2, 1.0)
    assert near(flat[0], 0.8) and near(flat[1], 0.8); n += 1
    assert all(0.0 <= v <= 1.0 for v in m.match_values([0.0, 1.0], 0.5, 5.0, 1.0)); n += 1
    assert raises(m.match_values, [0.1], 0.5, 0.1, 2.0); n += 1
    assert raises(m.mean_std, []); n += 1
    return n
