import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_batch_concat as m

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
    import _sy_batchtools as t
    ok(t.check_shape((2, 4, 5, 3)) == (2, 4, 5, 3))
    raises(t.check_shape, (4, 5, 3))
    raises(t.check_shape, (0, 4, 5, 3))
    p = t.concat_plan([(2, 8, 8, 3), (3, 4, 4, 3)], True)
    ok(p["total"] == 5 and p["height"] == 8 and p["width"] == 8 and p["channels"] == 3)
    raises(t.concat_plan, [(2, 8, 8, 3), (3, 4, 4, 3)], False)
    ok(t.concat_plan([(2, 8, 8, 3), (3, 8, 8, 4)], False)["total"] == 5)
    raises(t.concat_plan, [], True)
    ok(m.SYBatchConcat.RETURN_NAMES == ("images", "count"))
    return N[0]
