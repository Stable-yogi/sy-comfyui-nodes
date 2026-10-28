import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_frame_select as m

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
    ok(m.select_indices(10, 0, -1, 1) == list(range(10)))
    ok(m.select_indices(10, 2, 5, 1) == [2, 3, 4, 5])
    ok(m.select_indices(10, 0, 9, 3) == [0, 3, 6, 9])
    ok(m.select_indices(10, -3, -1, 1) == [7, 8, 9])
    ok(m.select_indices(10, -10, -1, 4) == [0, 4, 8])
    ok(m.select_indices(5, 3, 3, 1) == [3])
    ok(m.resolve_index(-1, 5, "x") == 4)
    raises(m.select_indices, 5, 0, 5, 1)
    raises(m.select_indices, 5, -6, -1, 1)
    raises(m.select_indices, 5, 3, 1, 1)
    raises(m.select_indices, 5, 0, 4, 0)
    raises(m.select_indices, 0, 0, 0, 1)
    return N[0]
