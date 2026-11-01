import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_roll_image as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    assert m.roll_index(0, 1, 5) == 1; n += 1
    assert m.roll_index(4, 1, 5) == 0; n += 1
    assert m.roll_index(0, -1, 5) == 4; n += 1
    assert m.roll_index(2, 0, 5) == 2; n += 1
    assert m.roll_index(2, 5, 5) == 2; n += 1
    assert m.roll_index(2, 12, 5) == 4; n += 1
    assert m.roll_index(2, -12, 5) == 0; n += 1
    assert m.roll_index(0, 8192, 1) == 0; n += 1
    row = list("abcde")
    rolled = [None] * 5
    for i, v in enumerate(row):
        rolled[m.roll_index(i, 2, 5)] = v
    assert rolled == list("deabc"); n += 1
    assert m.shift_pixels(30, "pixels", 100) == 30; n += 1
    assert m.shift_pixels(25, "percent", 200) == 50; n += 1
    assert m.shift_pixels(-50, "percent", 64) == -32; n += 1
    assert m.shift_pixels(100, "percent", 64) % 64 == 0; n += 1
    assert m.shift_pixels(8192, "percent", 10) == 819; n += 1
    msg = raises(m.shift_pixels, 1, "inches", 10)
    assert msg and "unit" in msg; n += 1
    assert raises(m.roll_index, 0, 1, 0); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYRollImage"] == "Roll Image SY"; n += 1
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
    _c(m.roll_amounts(10, 5, "pixels", 100, 50) == (10, 5))
    _c(m.roll_amounts(-10, -5, "pixels", 100, 50) == (90, 45))
    _c(m.roll_amounts(110, 55, "pixels", 100, 50) == (10, 5))
    _c(m.roll_amounts(25, 50, "percent", 200, 100) == (50, 50))
    _c(m.roll_amounts(0, 0, "pixels", 100, 51, True) == (50, 25))
    _c(m.roll_amounts(10, 0, "pixels", 100, 50, True) == (60, 25))
    _c(m.roll_amounts(100, 0, "percent", 64, 64) == (0, 0))
    _c(m.roll_amounts(0, 0, "pixels", 1, 1, True) == (0, 0))
    _r(m.roll_amounts, 1, 1, "inches", 10, 10)
    _r(m.roll_amounts, 1, 1, "pixels", 0, 10)
    _c("passed through" in m.roll_info(0, 0, 10, 10))
    _c("40 px to the right and 3 px down" in m.roll_info(40, 3, 100, 100))
    _c("px down" not in m.roll_info(40, 0, 100, 100) and "half-size" in m.roll_info(50, 25, 100, 50, True))
    _c(m.SYRollImage.RETURN_NAMES == ("image", "info") and "half_offset" in m.SYRollImage.INPUT_TYPES()["optional"])
    return (n) + _k[0]
