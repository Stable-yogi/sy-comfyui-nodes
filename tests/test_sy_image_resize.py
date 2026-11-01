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
    assert m.SYImageResize.RETURN_TYPES == ("IMAGE", "INT", "INT", "MASK", "STRING"); n += 1
    assert m.SYImageResize.RETURN_NAMES[-2:] == ("mask", "info"); n += 1
    # --- scale limit
    up = m.plan_resize(100, 100, 200, 200, "stretch", 1)
    down = m.plan_resize(100, 100, 50, 50, "stretch", 1)
    assert m.skip_reason(100, 100, up, "any") == "" and m.skip_reason(100, 100, down, "any") == ""
    assert "never enlarge" in m.skip_reason(100, 100, up, "never enlarge") and m.skip_reason(100, 100, down, "never enlarge") == ""
    assert "never shrink" in m.skip_reason(100, 100, down, "never shrink") and m.skip_reason(100, 100, up, "never shrink") == ""
    assert raises(m.skip_reason, 100, 100, up, "sideways")
    n += 5
    # --- megapixel cap
    assert m.cap_megapixels(1000, 1000, 4096, 4096, "stretch", 8, 0) == (4096, 4096, False)
    w, h, cap = m.cap_megapixels(1000, 1000, 4096, 4096, "stretch", 8, 1.0)
    po = m.plan_resize(1000, 1000, w, h, "stretch", 8)
    assert cap and po["out_w"] * po["out_h"] <= 1000000 and po["out_w"] % 8 == 0 and w > 900
    w, h, cap = m.cap_megapixels(1000, 1000, 512, 512, "stretch", 8, 1.0)
    assert (w, h, cap) == (512, 512, False)
    w, h, cap = m.cap_megapixels(2000, 1000, 4000, 4000, "pad", 64, 2.0)
    po = m.plan_resize(2000, 1000, w, h, "pad", 64)
    assert cap and po["out_w"] * po["out_h"] <= 4000000
    assert raises(m.cap_megapixels, 10, 10, 10, 10, "stretch", 1, -1)
    n += 5
    # --- size error and info
    big = m.plan_resize(10, 4000, 16384, 16384, "fill and crop", 1)
    assert raises(m.check_scaled, big)
    try:
        m.check_scaled(big)
    except ValueError as e:
        assert "16384" in str(e) and "pick a smaller size" in str(e)
    m.check_scaled(m.plan_resize(100, 100, 512, 512, "stretch", 8))
    n += 2
    t = m.resize_info(1000, 500, 512, 256, "fit inside")
    assert "Fit inside: 1000x500 -> 512x256" in t and "shape kept" in t and t.endswith(".")
    t = m.resize_info(1000, 500, 512, 512, "stretch")
    assert "squashed or stretched" in t
    assert "squashed" not in m.resize_info(100, 100, 200, 200, "stretch")
    assert "cut off" in m.resize_info(1000, 500, 512, 512, "fill and crop")
    assert "pad colour" in m.resize_info(1000, 500, 512, 512, "pad")
    t = m.resize_info(100, 100, 100, 100, "stretch", skipped="the picture is smaller")
    assert t.startswith("Left at 100x100") and "smaller" in t
    t = m.resize_info(1000, 500, 512, 256, "fit inside", capped=True, mask_note="the mask was resized with the picture")
    assert "max_megapixels" in t and "mask was resized" in t
    n += 7
    return n
