import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_frame_interpolate_blend as m

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
    ok(m.blend_weights(1) == [0.5])
    w = m.blend_weights(3)
    ok(len(w) == 3 and abs(w[0] - 0.25) < 1e-9 and abs(w[2] - 0.75) < 1e-9)
    raises(m.blend_weights, 0)
    p = m.interp_plan(3, 1)
    ok(len(p) == 5)
    ok(p == [(0, 0, 0.0), (0, 1, 0.5), (1, 1, 0.0), (1, 2, 0.5), (2, 2, 0.0)])
    ok(len(m.interp_plan(4, 2)) == 3 * 3 + 1)
    q = m.interp_plan(3, 1, True)
    ok(len(q) == 6 and q[-1] == (2, 0, 0.5))
    raises(m.interp_plan, 1, 1)
    raises(m.interp_plan, 5000, 4)
    return N[0]
