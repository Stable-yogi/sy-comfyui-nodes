import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_ref_image_size as m


def run():
    n = 0
    p = m.plan_size(1000, 1000, 864, 480, "pad to video shape")
    assert (p["out_w"], p["out_h"]) == (864, 480) and (p["scale_w"], p["scale_h"]) == (480, 480), p; n += 1
    assert p["pad"] == (192, 0, 192, 0) and p["crop"] is None, p; n += 1
    p = m.plan_size(1000, 1000, 864, 480, "fill video (crop)")
    assert (p["out_w"], p["out_h"]) == (864, 480) and p["crop"] == (0, 192, 864, 480), p; n += 1
    assert any("cut off" in t for t in p["notes"]), p["notes"]; n += 1
    p = m.plan_size(1000, 500, 864, 480, "fit inside video")
    assert (p["out_w"], p["out_h"]) == (864, 432) and p["pad"] is None and p["crop"] is None, p; n += 1
    p = m.plan_size(400, 300, 1280, 720, "keep shape", max_side=640)
    assert (p["out_w"], p["out_h"]) == (640, 480), p; n += 1
    assert any("capped" in t for t in p["notes"]) and any("bigger" in t for t in p["notes"]), p["notes"]; n += 1
    p = m.plan_size(480, 864, 864, 480, "pad to video shape")
    assert any("tall but the video is wide" in t for t in p["notes"]), p["notes"]; n += 1
    p = m.plan_size(777, 333, 801, 451, "fill video (crop)", multiple=32)
    assert p["out_w"] % 32 == 0 and p["out_h"] % 32 == 0, p; n += 1
    for bad in ((0, 10, 864, 480, "fit inside video"), (10, 10, 8, 480, "fit inside video"),
                (10, 10, 864, 480, "stretch"), (10, 10, 864, 480, "fit inside video", -1),
                (10, 10, 864, 480, "fit inside video", 0, 3)):
        try:
            m.plan_size(*bad)
            raise SystemExit("bad input must raise: %r" % (bad,))
        except ValueError:
            n += 1
    try:
        import torch
    except ImportError:
        return n
    img = torch.rand(2, 100, 100, 3)
    out, w, h, info = m.SYRefImageSize().run(img, 160, 96, "pad to video shape", 0, "black", 8)
    assert tuple(out.shape) == (2, 96, 160, 3) and (w, h) == (160, 96), out.shape; n += 1
    assert float(out[0, 50, 0].sum()) == 0.0 and "100x100 -> 160x96" in info, info; n += 1
    out, w, h, _ = m.SYRefImageSize().run(img, 160, 96, "fill video (crop)", 0, "edge", 8)
    assert tuple(out.shape) == (2, 96, 160, 3) and float(out.min()) >= 0.0 and float(out.max()) <= 1.0; n += 1
    out, _, _, _ = m.SYRefImageSize().run(img, 160, 96, "pad to video shape", 0, "edge", 8)
    assert tuple(out.shape) == (2, 96, 160, 3); n += 1
    try:
        m.SYRefImageSize().run(img, 160, 96, "pad to video shape", 0, "pink", 8)
        raise SystemExit("bad pad colour must raise")
    except ValueError:
        n += 1
    return n
