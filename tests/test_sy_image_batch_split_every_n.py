import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_image_batch_split_every_n as m

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
    ok(m.split_range(10, 4, 0) == (0, 4, 3))
    ok(m.split_range(10, 4, 1) == (4, 8, 3))
    ok(m.split_range(10, 4, 2) == (8, 10, 3))
    ok(m.split_range(8, 4, 1) == (4, 8, 2))
    ok(m.split_range(3, 100, 0) == (0, 3, 1))
    raises(m.split_range, 10, 4, 3)
    raises(m.split_range, 10, 4, -1)
    raises(m.split_range, 10, 0, 0)
    raises(m.split_range, 0, 4, 0)
    ok(m.SYImageBatchSplitEveryN.RETURN_TYPES[:3] == ("IMAGE", "INT", "INT"))
    ok(m.SYImageBatchSplitEveryN.RETURN_NAMES == ("images", "parts_total", "count", "start_index", "info"))
    # added value: wrap, pad, drop, info
    ok(m.plan_slice(10, 4, 2)[:4] == (8, 10, 3, 0))
    r = m.plan_slice(10, 4, 2)
    ok("Slice 3 of 3 (pictures 8 to 9 of 10)" in r[4] and "shorter than part_size (2 of 4)" in r[4])
    ok(m.plan_slice(10, 4, 3, wrap=True)[:3] == (0, 4, 3) and "wrapped round to slice 0" in m.plan_slice(10, 4, 3, wrap=True)[4])
    ok(m.plan_slice(10, 4, 7, wrap=True)[:2] == (4, 8))
    ok(m.plan_slice(10, 4, 2, False, "pad")[:4] == (8, 10, 3, 2))
    ok("repeated 2 times to fill 4" in m.plan_slice(10, 4, 2, False, "pad")[4])
    ok(m.plan_slice(8, 4, 1, False, "pad")[3] == 0)
    ok(m.plan_slice(10, 4, 1, False, "drop")[:3] == (4, 8, 2))
    ok("dropped" in m.plan_slice(10, 4, 1, False, "drop")[4])
    ok(m.plan_slice(10, 4, 2, True, "drop")[:2] == (0, 4))
    raises(m.plan_slice, 10, 4, 2, False, "drop")
    raises(m.plan_slice, 3, 4, 0, False, "drop")
    ok(m.plan_slice(3, 4, 0, False, "keep")[:3] == (0, 3, 1))
    raises(m.plan_slice, 10, 4, 3)
    for bad in ((10, 4, -1), (10, 0, 0), (0, 4, 0), (10, 4, 0, False, "x")):
        raises(m.plan_slice, *bad)
    try:
        m.plan_slice(10, 4, 9)
    except ValueError as e:
        ok("turn wrap on" in str(e) and "3 slices" in str(e))
    try:
        import torch
        node = m.SYImageBatchSplitEveryN()
        imgs = torch.arange(10, dtype=torch.float32).view(10, 1, 1, 1).expand(10, 2, 2, 3).clone()
        out = node.run(imgs, 4, 2, False, "pad")
        ok(out[0].shape[0] == 4 and out[2] == 4 and out[3] == 8 and float(out[0][3, 0, 0, 0]) == 9.0)
        out = node.run(imgs, 4, 5, True)
        ok(out[0].shape[0] == 4 and out[3] == 4 and out[1] == 3)
        out = node.run(imgs, 4, 2)
        ok(out[0].shape[0] == 2 and out[2] == 2)
    except ImportError:
        pass
    return N[0]
