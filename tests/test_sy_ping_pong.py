import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_ping_pong as m

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
    ok(m.pingpong_order(4) == [0, 1, 2, 3, 2, 1])
    ok(m.pingpong_order(4, True) == [0, 1, 2, 3, 3, 2, 1, 0])
    ok(m.pingpong_order(1) == [0])
    ok(m.pingpong_order(2) == [0, 1])
    ok(m.pingpong_order(2, True) == [0, 1, 1, 0])
    raises(m.pingpong_order, 0)
    return N[0]
