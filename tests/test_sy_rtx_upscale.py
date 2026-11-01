import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_rtx_upscale as m


def must_raise(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected a ValueError")


def run():
    n = 0
    assert m.plan_target(1920, 1080, "2x bigger") == ("scale", 2.0); n += 1
    assert m.plan_target(960, 540, "4x bigger") == ("scale", 4.0); n += 1
    assert m.plan_target(1920, 1080, "Height 2160 (4K)") == ("size", 3840, 2160); n += 1
    assert m.plan_target(1280, 720, "Height 1440 (QHD)") == ("size", 2560, 1440); n += 1
    assert m.plan_target(1000, 1000, "Height 1440 (QHD)") == ("size", 1440, 1440); n += 1
    w = m.plan_target(1001, 700, "Height 1440 (QHD)")[1]
    assert w % 8 == 0; n += 1  # the node steps in 8 pixels
    assert "limit" in must_raise(m.plan_target, 3840, 2160, "4x bigger"); n += 1
    assert "nothing to upscale" in must_raise(m.plan_target, 3840, 2160, "Height 1440 (QHD)"); n += 1
    assert "smaller" in must_raise(m.plan_target, 20, 20, "2x bigger"); n += 1
    assert "target" in must_raise(m.plan_target, 100, 100, "Huge"); n += 1
    assert m.resize_argument(("scale", 2.0)) == {"resize_type": "scale by multiplier", "scale": 2.0}; n += 1
    assert m.resize_argument(("size", 3840, 2160)) == {"resize_type": "target dimensions", "width": 3840, "height": 2160}; n += 1
    assert "Nvidia VFX" in m.MISSING and "RTX" in m.MISSING; n += 1
    t = m.info_text((1920, 1080), (3840, 2160), "ULTRA", ("size", 3840, 2160))
    assert t == "RTX upscale 1920x1080 -> 3840x2160, quality ULTRA (size)"; n += 1
    assert m.SYRtxUpscale.INPUT_TYPES()["required"]["target"][1]["default"] == "Height 2160 (4K)"; n += 1
    return n
