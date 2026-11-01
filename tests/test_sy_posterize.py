import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_posterize as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def near(a, b, eps=1e-9):
    return abs(a - b) < eps


def run():
    n = 0
    assert m.quantise(0.0, 2) == 0.0 and m.quantise(1.0, 2) == 1.0; n += 1
    assert m.quantise(0.4, 2) == 0.0 and m.quantise(0.6, 2) == 1.0; n += 1
    assert near(m.quantise(0.5, 3), 0.5); n += 1
    assert near(m.quantise(0.3, 4), 1 / 3.0) and near(m.quantise(0.7, 4), 2 / 3.0); n += 1
    assert m.quantise(1.0, 4) == 1.0 and m.quantise(0.0, 4) == 0.0; n += 1
    assert m.quantise(-0.5, 4) == 0.0 and m.quantise(2.0, 4) == 1.0; n += 1
    worst = max(abs(m.quantise(i / 1000.0, 256) - i / 1000.0) for i in range(1001))
    assert worst <= 1 / 255.0; n += 1
    assert all(m.quantise(i / 255.0, 256) == i / 255.0 or near(m.quantise(i / 255.0, 256), i / 255.0, 1e-9) for i in range(256)); n += 1
    outs = {m.quantise(i / 500.0, 5) for i in range(501)}
    assert outs == {0.0, 0.25, 0.5, 0.75, 1.0}; n += 1
    assert m.quantise(0.5, 2) == 1.0; n += 1  # halves round up
    # idempotent
    assert all(near(m.quantise(m.quantise(i / 97.0, 6), 6), m.quantise(i / 97.0, 6)) for i in range(98)); n += 1
    assert raises(m.quantise, 0.5, 1); n += 1
    assert raises(m.quantise, 0.5, 257); n += 1
    assert raises(m.check_levels, 0); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYPosterize"] == "Posterize SY"; n += 1
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
    _i = m.posterize_info(4)
    _c("4 levels per colour channel" in _i and "0.00, 0.33, 0.67, 1.00" in _i and "at most 64" in _i and "almost like" not in _i)
    _c("0.00, 0.50, 1.00" not in m.posterize_info(2) and "0.00, 1.00" in m.posterize_info(2) and "at most 8 " in m.posterize_info(2))
    _c("..." in m.posterize_info(16) and "1.00" in m.posterize_info(16))
    _c("almost like" in m.posterize_info(256))
    _r(m.posterize_info, 1)
    _c(m.SYPosterize.RETURN_NAMES == ("image", "info"))
    return (n) + _k[0]
