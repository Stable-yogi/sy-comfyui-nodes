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
    # added value: seconds and info
    ids = m.rate_convert_indices(24, 24, 16)
    sec, info = m.convert_info(24, ids, 24, 16)
    ok(sec == 1.0 and "24 frames at 24 fps (1 s) became 16 frames at 16 fps (1 s)" in info and "8 frames were dropped" in info and "repeated" not in info)
    ids = m.rate_convert_indices(12, 12, 24)
    sec, info = m.convert_info(12, ids, 12, 24)
    ok(sec == 1.0 and "12 frames were repeated" in info and "dropped" not in info)
    ids = m.rate_convert_indices(10, 24, 24)
    sec, info = m.convert_info(10, ids, 24, 24)
    ok("Every frame was kept once" in info and "nothing changed" in info)
    ok(m.convert_info(4, [0, 2], 24, 12)[0] == round(2 / 12, 3))
    ok(m.SYFrameRateConvert.RETURN_NAMES == ("images", "count", "fps", "seconds", "info"))
    ok(len(m.SYFrameRateConvert.RETURN_TYPES) == 5)
    try:
        import torch
        out = m.SYFrameRateConvert().run(torch.zeros(24, 4, 4, 3), 24.0, 16.0)
        ok(out[0].shape[0] == 16 and out[1] == 16 and out[2] == 16.0 and out[3] == 1.0 and "dropped" in out[4])
    except ImportError:
        pass
    return N[0]
