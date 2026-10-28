import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_batch_repeat as m

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
    ok(m.repeat_indices(3, 2, "each_picture") == [0, 0, 1, 1, 2, 2])
    ok(m.repeat_indices(3, 2, "whole_batch") == [0, 1, 2, 0, 1, 2])
    ok(m.repeat_indices(2, 1, "each_picture") == [0, 1])
    raises(m.repeat_indices, 0, 2, "each_picture")
    raises(m.repeat_indices, 3, 0, "each_picture")
    raises(m.repeat_indices, 3, 2, "sideways")
    raises(m.repeat_indices, 100, 256, "whole_batch")
    return N[0]
