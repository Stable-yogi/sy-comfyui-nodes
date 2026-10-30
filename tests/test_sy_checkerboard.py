import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_checkerboard as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    assert m.checker_is_a(0, 0, 4) is True; n += 1
    assert m.checker_is_a(3, 3, 4) is True; n += 1
    assert m.checker_is_a(4, 0, 4) is False; n += 1
    assert m.checker_is_a(0, 4, 4) is False; n += 1
    assert m.checker_is_a(4, 4, 4) is True; n += 1
    assert m.checker_is_a(7, 0, 4) is False; n += 1
    assert m.checker_is_a(8, 0, 4) is True; n += 1
    assert [m.checker_is_a(x, 0, 1) for x in range(4)] == [True, False, True, False]; n += 1
    assert m.checker_is_a(100, 100, 1000) is True; n += 1
    assert raises(m.checker_is_a, 0, 0, 0); n += 1
    msg = raises(m.check_sizes, 0, 10, 4, 1)
    assert msg and "width" in msg; n += 1
    msg = raises(m.check_sizes, 10, 0, 4, 1)
    assert msg and "height" in msg; n += 1
    msg = raises(m.check_sizes, 10, 10, 0, 1)
    assert msg and "cell" in msg; n += 1
    msg = raises(m.check_sizes, 10, 10, 4, 0)
    assert msg and "batch_size" in msg; n += 1
    assert m.check_sizes(1, 1, 1, 1) is None; n += 1
    assert m.DEFAULT_A.startswith("#") and len(m.DEFAULT_A) == 7; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYCheckerboard"] == "Checkerboard SY"; n += 1
    return n
