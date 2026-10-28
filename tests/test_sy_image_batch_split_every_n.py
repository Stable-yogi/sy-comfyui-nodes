import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_image_batch_split_every_n as m

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
    ok(m.split_range(10, 4, 0) == (0, 4, 3))
    ok(m.split_range(10, 4, 1) == (4, 8, 3))
    ok(m.split_range(10, 4, 2) == (8, 10, 3))
    ok(m.split_range(8, 4, 1) == (4, 8, 2))
    ok(m.split_range(3, 100, 0) == (0, 3, 1))
    raises(m.split_range, 10, 4, 3)
    raises(m.split_range, 10, 4, -1)
    raises(m.split_range, 10, 0, 0)
    raises(m.split_range, 0, 4, 0)
    ok(m.SYImageBatchSplitEveryN.RETURN_TYPES == ("IMAGE", "INT", "INT"))
    return N[0]
