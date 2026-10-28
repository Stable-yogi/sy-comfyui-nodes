import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_reverse_batch as m

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
    ok(m.reverse_indices(4) == [3, 2, 1, 0])
    ok(m.reverse_indices(1) == [0])
    raises(m.reverse_indices, 0)
    ok(m.SYReverseBatch.RETURN_TYPES == ("IMAGE",))
    return N[0]
