import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_invert_threshold as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def dot(h, w, x, y, v=1.0):
    r = [[0.0] * w for _ in range(h)]
    r[y][x] = v
    return r


def run():
    n = 0
    a = [[0.0, 0.3, 0.5, 1.0]]
    assert m.invert_threshold(a, False, False, 0.5) == a
    assert m.invert_threshold(a, True, False, 0.5) == [[1.0, 0.7, 0.5, 0.0]]
    assert m.invert_threshold(a, False, True, 0.5) == [[0.0, 0.0, 1.0, 1.0]]
    assert m.invert_threshold(a, True, True, 0.5) == [[1.0, 1.0, 0.0, 0.0]]
    n += 4
    assert m.invert_threshold(a, False, True, 0.0) == [[1.0, 1.0, 1.0, 1.0]]
    assert m.invert_threshold(a, False, True, 1.0) == [[0.0, 0.0, 0.0, 1.0]]
    n += 2
    assert raises(m.invert_threshold, a, True, True, 1.5)
    n += 1
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
    _c("unchanged" in m.invert_info(False, False, 0.5, 10, 100))
    _c("cut at 0.30" in m.invert_info(False, True, 0.3, 10, 100))
    _c("then flipped" in m.invert_info(True, True, 0.3, 10, 100))
    _c("flipped" in m.invert_info(True, False, 0.3, 10, 100) and "cut" not in m.invert_info(True, False, 0.3, 10, 100))
    _c("all black" in m.invert_info(True, False, 0.5, 0, 100))
    _c("all white" in m.invert_info(True, False, 0.5, 100, 100))
    _c("10.0%" in m.invert_info(True, False, 0.5, 10, 100))
    _c(m.SYMaskInvertThreshold.RETURN_NAMES == ("mask", "info") and len(m.SYMaskInvertThreshold.RETURN_TYPES) == 2)
    return (n) + _k[0]
