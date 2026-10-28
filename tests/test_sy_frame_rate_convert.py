import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_frame_rate_convert as m

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
    ok(m.rate_convert_indices(24, 24, 24) == list(range(24)))
    ok(m.rate_convert_indices(4, 24, 12) == [0, 2])
    r = m.rate_convert_indices(3, 12, 24)
    ok(len(r) == 6 and r[0] == 0 and r[-1] == 2 and r == sorted(r))
    ok(len(m.rate_convert_indices(24, 24, 16)) == 16)
    ok(max(m.rate_convert_indices(10, 30, 60)) <= 9)
    ok(m.rate_convert_indices(1, 30, 10) == [0])
    raises(m.rate_convert_indices, 0, 24, 16)
    raises(m.rate_convert_indices, 5, 0, 16)
    raises(m.rate_convert_indices, 5, 24, float("nan"))
    raises(m.rate_convert_indices, 100000, 1, 1000)
    return N[0]
