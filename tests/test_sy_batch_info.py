import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_batch_info as m

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
    ok(m.describe_batch((4, 512, 768, 3)) == (4, 768, 512, 3, "4 pictures, 768x512, 3 channels"))
    ok(m.describe_batch((1, 8, 8, 4))[4] == "1 picture, 8x8, 4 channels")
    raises(m.describe_batch, (8, 8, 3))
    raises(m.describe_batch, (0, 8, 8, 3))
    return N[0]
