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
    _k = [0]
    def _c(cond, msg="d3 check failed"):
        _k[0] += 1
        if not cond:
            raise AssertionError(msg)
    def _r(fn, *a):
        _k[0] += 1
        try:
            fn(*a)
        except ValueError as e:
            return str(e)
        raise AssertionError("expected ValueError for %r" % (a,))
    _c("8 frames became 14 frames" in m.pingpong_info(8) and "smooth" in m.pingpong_info(8))
    _c("8 frames became 16 frames" in m.pingpong_info(8, True) and "twice" in m.pingpong_info(8, True))
    _c("nothing to play backwards" in m.pingpong_info(1))
    _c("same as the input" in m.pingpong_info(2))
    _c("same as the input" not in m.pingpong_info(2, True))
    _r(m.pingpong_info, 0)
    _c(m.SYPingPong.RETURN_NAMES == ("images", "count", "info") and len(m.SYPingPong.RETURN_TYPES) == 3)
    return (N[0]) + _k[0]
