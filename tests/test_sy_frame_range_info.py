import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_frame_range_info as m

N = [0]


def ok(cond, msg="check failed"):
    N[0] += 1
    if not cond:
        raise AssertionError(msg)


def raises(fn, *args):
    N[0] += 1
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError("expected ValueError for %r" % (args,))


def run():
    ok(m.range_info(0, 8, 2) == ("0, 2, 4, 6, 8", 5, 8))
    ok(m.range_info(0, 7, 2) == ("0, 2, 4, 6", 4, 6))
    ok(m.range_info(5, 5, 1) == ("5", 1, 5))
    ok(m.range_info(10, 4, 3) == ("10, 7, 4", 3, 4))
    ok(m.frame_range(0, 3, 1) == [0, 1, 2, 3])
    raises(m.frame_range, 0, 10, 0)
    raises(m.frame_range, 0, 10000000, 1)
    ok(m.SYFrameRangeInfo().run(1, 3, 1) == ("1, 2, 3", 3, 3))
    return N[0]
