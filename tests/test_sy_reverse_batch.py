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
    ok(m.SYReverseBatch.RETURN_TYPES[:1] == ("IMAGE",))
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
    _c("Reversed 5 pictures" in m.reverse_info(5) and "old picture 5" in m.reverse_info(5))
    _c("changes nothing" in m.reverse_info(1))
    _r(m.reverse_info, 0)
    _c(m.SYReverseBatch.RETURN_NAMES == ("images", "count", "info") and len(m.SYReverseBatch.RETURN_TYPES) == 3)
    return (N[0]) + _k[0]
