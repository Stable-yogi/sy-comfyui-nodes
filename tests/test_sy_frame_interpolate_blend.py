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
    ok(m.new_fps(16, 1) == 32.0 and m.new_fps(24, 3) == 96.0 and m.new_fps(0, 2) == 0.0)
    raises(m.new_fps, -1, 1)
    t = m.blend_info(10, 1, False, 19, 16.0, 512, 512)
    ok("10 frames -> 19 frames" in t and "frame rate to 32 (was 16)" in t and "512x512" in t and "MB" in t)
    ok("enter your frame rate" in m.blend_info(10, 1, True, 20, 0.0, 64, 64) and "last blends into first" in m.blend_info(10, 1, True, 20, 0.0, 64, 64))
    ok("lot" in m.blend_info(100, 1, False, 199, 0.0, 2048, 2048) and "lot" not in m.blend_info(3, 1, False, 5, 0.0, 64, 64))
    ok(m.SYFrameInterpolateBlend.RETURN_NAMES == ("images", "count", "new_fps", "info"))
    return N[0]
