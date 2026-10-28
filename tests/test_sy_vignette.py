import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_vignette as m


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
    assert near(m.vignette_factor(49.5, 49.5, 100, 100, 1.0, 0.5), 1.0); n += 1
    assert m.vignette_factor(0, 0, 100, 100, 1.0, 0.5) < 0.05; n += 1
    assert near(m.vignette_factor(0, 0, 100, 100, 0.0, 0.5), 1.0); n += 1
    mid = m.vignette_factor(10, 50, 100, 100, 0.5, 0.5)
    assert m.vignette_factor(0, 0, 100, 100, 0.5, 0.5) < mid <= 1.0; n += 1
    a = m.vignette_factor(5, 50, 100, 100, 0.8, 0.3)
    b = m.vignette_factor(94, 50, 100, 100, 0.8, 0.3)
    assert near(a, b, 1e-9); n += 1
    assert m.vignette_factor(5, 5, 100, 100, 0.8, 0.05) <= m.vignette_factor(5, 5, 100, 100, 0.4, 0.05); n += 1
    assert raises(m.vignette_factor, 0, 0, 10, 10, 1.5, 0.5); n += 1
    assert raises(m.vignette_factor, 0, 0, 10, 10, 0.5, 0.0); n += 1
    assert raises(m.vignette_factor, 0, 0, 0, 10, 0.5, 0.5); n += 1
    return n
