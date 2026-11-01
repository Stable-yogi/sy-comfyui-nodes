import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_pad_image as m


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
    assert m.padded_size(10, 20, 1, 2, 3, 4) == (13, 27); n += 1
    mask = m.padded_mask(2, 2, 1, 0, 1, 0)
    assert mask == [[1.0, 1.0, 1.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0]]; n += 1
    assert len(mask) == 3 and len(mask[0]) == 3; n += 1
    zero = m.padded_mask(2, 2, 0, 0, 0, 0)
    assert sum(sum(r) for r in zero) == 0.0; n += 1
    assert sum(sum(r) for r in m.padded_mask(4, 4, 2, 2, 2, 2)) == 64 - 16; n += 1
    assert raises(m.padded_size, 10, 10, -1, 0, 0, 0); n += 1
    assert raises(m.padded_size, 0, 10, 0, 0, 0, 0); n += 1
    assert m.parse_colour("white") == (1.0, 1.0, 1.0); n += 1
    assert m.parse_colour("white", "255, 0, 51")[2] == 51 / 255.0; n += 1
    assert raises(m.parse_colour, "white", "1,2"); n += 1
    assert raises(m.parse_colour, "white", "1,2,300"); n += 1
    assert raises(m.parse_colour, "pink"); n += 1
    assert m.SYPadImage.RETURN_TYPES [:4] == ("IMAGE", "MASK", "INT", "INT"); n += 1
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
    _c(m.snap_extra(100, 8) == 4 and m.snap_extra(96, 8) == 0 and m.snap_extra(7, 1) == 0 and m.snap_extra(1, 64) == 63)
    _c("multiple_of" in _r(m.snap_extra, 10, 0))
    _i = m.pad_info(512, 512, 64, 64, 0, 0)
    _c("Padded 512x512 to 640x512" in _i and "extra" not in _i and "megapixels" not in _i)
    _c("3 px right and 5 px bottom extra" in m.pad_info(100, 100, 0, 3, 0, 5, 3, 5))
    _c("too big" in m.pad_info(4000, 4000, 100, 100, 100, 100))
    _r(m.pad_info, 10, 10, -1, 0, 0, 0)
    _c(m.SYPadImage.RETURN_NAMES == ("image", "mask", "width", "height", "info") and "multiple_of" in m.SYPadImage.INPUT_TYPES()["optional"])
    return (n) + _k[0]
