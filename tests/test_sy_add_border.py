import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_add_border as m
import _sy_hexcolour as hx


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    assert m.border_ring(0, 0, 10, 10, 1) is True; n += 1
    assert m.border_ring(5, 5, 10, 10, 1) is False; n += 1
    assert m.border_ring(9, 5, 10, 10, 1) is True; n += 1
    assert m.border_ring(5, 9, 10, 10, 1) is True; n += 1
    assert m.border_ring(1, 1, 10, 10, 1) is False; n += 1
    assert m.border_ring(1, 1, 10, 10, 2) is True; n += 1
    assert m.border_ring(5, 5, 10, 10, 0) is False; n += 1
    assert m.border_ring(0, 0, 1, 1, 0) is False; n += 1
    assert all(m.border_ring(x, y, 6, 8, 3) for x in range(6) for y in range(8)); n += 1
    assert all(m.border_ring(0, y, 1, 5, 1) for y in range(5)); n += 1
    ring = sum(m.border_ring(x, y, 8, 8, 2) for x in range(8) for y in range(8))
    assert ring == 64 - 16; n += 1
    msg = raises(m.border_ring, 0, 0, 5, 5, -1)
    assert msg and "size" in msg; n += 1
    assert raises(m.border_ring, 0, 0, 0, 5, 1); n += 1
    assert raises(m.check_mode, "middle"); n += 1
    assert m.check_mode("inside") is None; n += 1
    assert hx.parse_hex(m.DEFAULT_COLOUR) == (0.0, 0.0, 0.0); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYAddBorder"] == "Add Border SY"; n += 1
    return n
