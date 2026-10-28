import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_batch_list as m

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
    ok(m.split_indices(3) == [0, 1, 2])
    raises(m.split_indices, 0)
    ok(m.first_value([True]) is True)
    ok(m.first_value([False]) is False)
    ok(m.first_value(True) is True)
    ok(m.first_value([], 7) == 7)
    ok(m.SYBatchToList.OUTPUT_IS_LIST == (True,))
    ok(m.SYListToBatch.INPUT_IS_LIST is True)
    ok(not getattr(m.SYListToBatch, "OUTPUT_IS_LIST", None))
    return N[0]
