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
    return n
