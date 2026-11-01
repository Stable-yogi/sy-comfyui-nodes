import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_image_blend as m


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
    assert m.blend_value(0.3, 0.8, "normal") == 0.8; n += 1
    assert near(m.blend_value(0.5, 0.4, "multiply"), 0.2); n += 1
    assert near(m.blend_value(0.5, 0.5, "screen"), 0.75); n += 1
    assert near(m.blend_value(0.25, 0.5, "overlay"), 0.25); n += 1
    assert near(m.blend_value(0.75, 0.5, "overlay"), 0.75); n += 1
    assert m.blend_value(0.8, 0.5, "add") == 1.0; n += 1
    assert near(m.blend_value(0.2, 0.9, "difference"), 0.7); n += 1
    assert near(m.blend_with_opacity(0.2, 1.0, "normal", 0.5), 0.6); n += 1
    assert m.blend_with_opacity(0.2, 1.0, "normal", 0.0) == 0.2; n += 1
    assert m.blend_with_opacity(0.2, 0.9, "normal", 1.0) == 0.9; n += 1
    assert m.blend_with_opacity(1.0, 1.0, "add", 1.0) == 1.0; n += 1
    assert raises(m.blend_value, 0.1, 0.1, "burn"); n += 1
    assert raises(m.blend_with_opacity, 0.1, 0.1, "normal", 1.5); n += 1
    t = m.blend_info("multiply", 0.5, (512, 512), (512, 512), "stretch", False, False, False, 1, 1)
    assert t == "Blended with multiply at opacity 0.5."; n += 1
    t = m.blend_info("normal", 1.0, (1024, 512), (512, 512), "stretch", False, False, False, 1, 1)
    assert "stretched to 1024x512" in t and "shape changed" in t and "fill and crop" in t; n += 1
    t = m.blend_info("normal", 1.0, (1024, 1024), (512, 512), "stretch", False, False, False, 1, 1)
    assert "stretched" in t and "shape changed" not in t; n += 1
    t = m.blend_info("normal", 1.0, (1024, 512), (512, 512), "fill and crop", True, True, True, 4, 1)
    assert "cover 1024x512" in t and "transparency was used" in t and "inside the mask" in t and "repeated or trimmed" in t; n += 1
    assert "ignored" in m.blend_info("normal", 1.0, (8, 8), (8, 8), "stretch", False, False, True, 1, 1); n += 1
    assert m.check_fit("stretch") is None and raises(m.check_fit, "zoom"); n += 1
    assert m.SYImageBlend.RETURN_NAMES == ("image", "info"); n += 1
    assert list(m.SYImageBlend.INPUT_TYPES()["optional"]) == ["top_fit", "use_top_alpha", "mask"]; n += 1
    assert m.d2.cover_crop_plan(512, 512, 1024, 512) == (1024, 1024, 0, 256); n += 1
    assert m.d2.cover_crop_plan(1000, 500, 512, 512) == (1024, 512, 256, 0); n += 1
    try:
        import torch
    except ImportError:
        torch = None
    if torch is not None:
        a = torch.rand(2, 8, 8, 4)
        b = torch.rand(2, 8, 8, 3)
        out = m.blend_tensors(a, b, "normal", 0.5)
        assert out.shape == (2, 8, 8, 4) and torch.equal(out[..., 3], a[..., 3]); n += 1
        a3 = torch.rand(1, 8, 8, 3)
        assert m.blend_tensors(a3, b[:1], "multiply", 0.5).shape[3] == 3; n += 1
        assert m.blend_tensors(a, torch.rand(2, 8, 8, 4), "add", 1.0).shape[3] == 4; n += 1
    return n
