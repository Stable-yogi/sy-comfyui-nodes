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
    assert m.SYPadImage.RETURN_TYPES == ("IMAGE", "MASK", "INT", "INT"); n += 1
    return n
