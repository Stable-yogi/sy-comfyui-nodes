import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_crossfade_slideshow as m


def raises(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0

    def ok(cond, msg="check failed"):
        nonlocal n
        n += 1
        if not cond:
            raise SystemExit("crossfade slideshow: " + msg)

    p = m.plan_frames(3, 4, 2, False)
    ok(len(p) == 3 * 4 + 2 * 2 == m.frame_count(3, 4, 2, False), "length no loop")
    ok(p[0] == (0, 0, 0.0) and p[3] == (0, 0, 0.0), "first hold")
    ok(p[4][:2] == (0, 1) and p[5][:2] == (0, 1), "first fade pair")
    ok(0.0 < p[4][2] < p[5][2] < 1.0, "mix rises inside the fade")
    ok(p[-1] == (2, 2, 0.0), "ends on a hold without loop")
    pl = m.plan_frames(3, 4, 2, True)
    ok(len(pl) == 3 * 4 + 3 * 2 == m.frame_count(3, 4, 2, True), "length loop")
    ok(pl[-1][:2] == (2, 0), "loop fades last into first")
    ok(m.plan_frames(1, 5, 3, False) == [(0, 0, 0.0)] * 5, "single slide")
    ok(m.plan_frames(2, 3, 0, False) == [(0, 0, 0.0)] * 3 + [(1, 1, 0.0)] * 3, "zero fade is a hard cut")
    ok(raises(m.plan_frames, 0, 4, 2), "no pictures")
    ok(raises(m.plan_frames, 3, 0, 0), "hold zero")
    ok(raises(m.plan_frames, 3, 4, 5), "fade bigger than hold")
    ok(raises(m.plan_frames, 3, 4, -1), "negative fade")
    ok(m.eased_mix(0.5, True) == 0.5 and m.eased_mix(0.25, False) == 0.25, "ease values")
    ok(m.eased_mix(0.25, True) < 0.25, "ease starts slowly")
    ok(m.smoothstep(-1) == 0.0 and m.smoothstep(2) == 1.0, "smoothstep clamps")
    ok("5 pictures" in m.slideshow_info(5, 24, 12, False, 10), "info text")
    ok(m.SYCrossfadeSlideshow.RETURN_TYPES == ("IMAGE", "INT", "STRING"), "return types")
    ok(m.NODE_DISPLAY_NAME_MAPPINGS["SYCrossfadeSlideshow"] == "Crossfade Slideshow SY", "registered")
    ok("SYCrossfadeSlideshow" in m.NODE_CLASS_MAPPINGS, "class mapping")

    try:
        import torch
    except ImportError:
        torch = None
    if torch is not None:
        imgs = torch.zeros(3, 4, 6, 3)
        imgs[1] = 1.0
        imgs[2] = 0.5
        node = m.SYCrossfadeSlideshow()
        out, count, info = node.run(imgs, 3, 2, False, True)
        ok(out.shape == (3 * 3 + 2 * 2, 4, 6, 3) and count == out.shape[0], "tensor shape")
        ok(float(out[0].max()) == 0.0 and float(out[3 + 2].min()) == 1.0, "holds are exact slides")
        mid = float(out[3, 0, 0, 0])
        ok(0.0 < mid < 0.5, "fade frame is a blend")
        out2, c2, _ = node.run(imgs, 3, 2, True, False)
        ok(c2 == 3 * 3 + 3 * 2, "loop frame count")
        ok(float(out2[-2, 0, 0, 0]) > float(out2[-1, 0, 0, 0]) > 0.0, "loop fade heads to first slide")
        try:
            node.run(imgs, 3, 5, False, True)
            ok(False, "should raise")
        except ValueError:
            ok(True)
    return n
