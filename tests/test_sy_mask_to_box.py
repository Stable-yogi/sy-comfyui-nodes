import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_to_box as m


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


def blockmask(w, h, x0, y0, x1, y1):
    return [[1.0 if x0 <= x <= x1 and y0 <= y <= y1 else 0.0 for x in range(w)] for y in range(h)]


def run():
    n = 0
    k = blockmask(10, 8, 3, 2, 5, 4)
    assert m.mask_to_box(k, 0, 0.5, "error") == (3, 2, 3, 3)
    assert m.mask_to_box(k, 1, 0.5, "error") == (2, 1, 5, 5)
    n += 2
    assert m.mask_to_box(k, 100, 0.5, "error") == (0, 0, 10, 8)  # padding clamped to the image
    edge = blockmask(10, 8, 0, 0, 1, 1)
    assert m.mask_to_box(edge, 3, 0.5, "error") == (0, 0, 5, 5)
    n += 2
    assert m.mask_to_box(blockmask(10, 8, 9, 7, 9, 7), 2, 0.5, "error") == (7, 5, 3, 3)
    n += 1
    empty = blockmask(10, 8, 5, 5, 4, 4)
    assert m.mask_to_box(empty, 4, 0.5, "whole_image") == (0, 0, 10, 8)
    assert raises(m.mask_to_box, empty, 0, 0.5, "error")
    n += 2
    soft = [[0.2, 0.9]]
    assert m.mask_to_box(soft, 0, 0.5, "error") == (1, 0, 1, 1)
    assert m.mask_to_box(soft, 0, 0.1, "error") == (0, 0, 2, 1)
    n += 2
    assert raises(m.mask_to_box, k, -1, 0.5, "error") and raises(m.mask_to_box, k, 0, 0.5, "bogus")
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
    _k0 = (3, 2, 3, 3)
    _c(m.finish_box(_k0, 0, "error", 10, 8) == (3, 2, 3, 3, False))
    b = m.finish_box(_k0, 0, "error", 40, 40, 8)
    _c(b[2] % 8 == 0 and b[3] % 8 == 0 and b[4] is False)
    _c(b[0] >= 0 and b[1] >= 0 and b[0] + b[2] <= 40 and b[1] + b[3] <= 40)
    _c(m.finish_box(None, 0, "whole_image", 10, 8, 8) == (0, 0, 10, 8, True))
    _c("empty" in _r(m.finish_box, None, 0, "error", 10, 8))
    _c("multiple_of" in _r(m.finish_box, _k0, 0, "error", 10, 8, 0))
    _c("whole 10x8 image" in m.box_info(0, 0, 10, 8, 10, 8, True))
    _c("x=3, y=2, size 3x3" in m.box_info(3, 2, 3, 3, 10, 8, False) and "padding" not in m.box_info(3, 2, 3, 3, 10, 8, False))
    _c("padding 2" in m.box_info(3, 2, 3, 3, 10, 8, False, 2) and "multiple of 8" in m.box_info(3, 2, 3, 3, 10, 8, False, 0, 8))
    _c(m.SYMaskToBox.RETURN_NAMES[:4] == ("x", "y", "width", "height") and m.SYMaskToBox.RETURN_NAMES[4] == "info" and len(m.SYMaskToBox.RETURN_TYPES) == 5)
    return (n) + _k[0]
