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
    _c(m.unsharp_value(0.5, 0.4, 1.0) == m.unsharp_value(0.5, 0.4, 1.0, 0.0))
    _c(abs(m.unsharp_value(0.5, 0.49, 1.0, 0.05) - 0.5) < 1e-12)
    _c(abs(m.unsharp_value(0.5, 0.4, 1.0, 0.05) - 0.6) < 1e-9)
    _c(m.sharpen_line([0.5, 0.5, 0.5], 1.0, 2.0, 0.1) == [0.5, 0.5, 0.5])
    _c(m.sharpen_line([0.2, 0.2, 0.8, 0.8], 1.0, 1.0) != m.sharpen_line([0.2, 0.2, 0.8, 0.8], 1.0, 1.0, 0.9))
    _r(m.sharpen_line, [0.1, 0.2], 1.0, 1.0, 2.0)
    _c("nothing was sharpened" in m.sharpen_info(1.0, 0.0))
    _i = m.sharpen_info(1.5, 1.0)
    _c("1.5 px" in _i and "strength 1.00" in _i and "ignoring" not in _i and "halos" not in _i)
    _c("ignoring brightness differences below 0.02" in m.sharpen_info(1.0, 1.0, 0.02))
    _c("halos" in m.sharpen_info(1.0, 3.0))
    _r(m.sharpen_info, -1, 1)
    _r(m.sharpen_info, 1, 1, -0.1)
    _c(m.SYSharpen.RETURN_NAMES == ("image", "info") and "threshold" in m.SYSharpen.INPUT_TYPES()["optional"])
    return (n) + _k[0]
