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
    _c(abs(m.vignette_factor(3, 4, 10, 10, 0.5, 0.5) - m.vignette_factor(3, 4, 10, 10, 0.5, 0.5, 0.5, 0.5)) < 1e-12)
    _c(m.vignette_factor(0, 0, 10, 10, 0.8, 0.5, 0.0, 0.0) > 0.99)
    _c(m.vignette_factor(9, 9, 10, 10, 0.8, 0.5, 0.0, 0.0) < m.vignette_factor(0, 0, 10, 10, 0.8, 0.5, 0.0, 0.0))
    _c(m.vignette_factor(5, 5, 11, 11, 1.0, 0.5, 0.5, 0.5) == 1.0)
    _r(m.vignette_factor, 1, 1, 10, 10, 0.5, 0.5, 1.2, 0.5)
    _r(m.vignette_factor, 1, 1, 10, 10, 0.5, 0.5, 0.5, -0.1)
    _c("not darkened" in m.vignette_info(0.0, 0.5))
    _i = m.vignette_info(0.5, 0.4)
    _c("up to 50%" in _i and "in the middle" in _i and "fully black" not in _i)
    _c("20% across, 30% down" in m.vignette_info(0.5, 0.4, 0.2, 0.3) and "fully black" in m.vignette_info(1.0, 0.4))
    _r(m.vignette_info, 1.5, 0.5)
    _c(m.SYVignette.RETURN_NAMES == ("image", "info") and set(m.SYVignette.INPUT_TYPES()["optional"]) == {"centre_x", "centre_y"})
    return (n) + _k[0]
