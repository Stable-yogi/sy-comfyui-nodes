import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_image_resize as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def near(a, b, eps=1e-6):
    return abs(a - b) < eps


def run():
    n = 0
    p = m.plan_resize(1000, 500, 512, 512, "stretch", 1)
    assert (p["out_w"], p["out_h"]) == (512, 512); n += 1
    p = m.plan_resize(1000, 500, 512, 512, "fit inside", 1)
    assert (p["out_w"], p["out_h"]) == (512, 256); n += 1
    p = m.plan_resize(1000, 500, 512, 512, "fit inside", 64)
    assert (p["out_w"], p["out_h"]) == (512, 256); n += 1
    p = m.plan_resize(1000, 700, 512, 512, "fit inside", 64)
    assert p["out_w"] % 64 == 0 and p["out_h"] % 64 == 0 and p["out_w"] <= 512; n += 1
    p = m.plan_resize(1000, 500, 512, 512, "fill and crop", 1)
    assert (p["scaled_w"], p["scaled_h"]) == (1024, 512) and p["crop_x"] == 256 and p["crop_y"] == 0; n += 1
    assert (p["out_w"], p["out_h"]) == (512, 512); n += 1
    p = m.plan_resize(1000, 500, 512, 512, "pad", 1)
    assert (p["scaled_w"], p["scaled_h"]) == (512, 256) and p["pad_y"] == 128 and p["pad_x"] == 0; n += 1
    assert (p["out_w"], p["out_h"]) == (512, 512); n += 1
    p = m.plan_resize(100, 100, 1000, 1000, "stretch", 8)
    assert p["out_w"] == 1000 and p["out_w"] % 8 == 0; n += 1
    assert m.round_multiple(3, 8) == 8 and m.round_multiple(100, 64) == 128 and m.round_multiple(100, 64, down=True) == 64; n += 1
    assert raises(m.plan_resize, 10, 10, 10, 10, "zoom", 1); n += 1
    assert raises(m.plan_resize, 0, 10, 10, 10, "stretch", 1); n += 1
    assert raises(m.round_multiple, 10, 0); n += 1
    assert m.SYImageResize.RETURN_TYPES == ("IMAGE", "INT", "INT"); n += 1
    return n
