import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_remove_background as m


def refuses(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    return None


def close(a, b, eps=1e-5):
    return abs(a - b) <= eps


def run():
    n = 0
    # ---- grow_amount_ok / feather_ok
    assert m.grow_amount_ok(0) == 0 and m.grow_amount_ok(64) == 64 and m.grow_amount_ok(-64) == -64; n += 1
    assert m.grow_amount_ok(5.0) == 5; n += 1
    assert "between -64 and 64" in refuses(m.grow_amount_ok, 65); n += 1
    assert "between -64 and 64" in refuses(m.grow_amount_ok, -65); n += 1
    assert "whole number" in refuses(m.grow_amount_ok, 1.5); n += 1
    assert "whole number" in refuses(m.grow_amount_ok, "x"); n += 1
    assert "whole number" in refuses(m.grow_amount_ok, None); n += 1
    assert "whole number" in refuses(m.grow_amount_ok, True); n += 1
    assert m.feather_ok(0) == 0 and m.feather_ok(64) == 64; n += 1
    assert "feather" in refuses(m.feather_ok, -1); n += 1
    assert "feather" in refuses(m.feather_ok, 65); n += 1
    # ---- colour_for
    assert m.colour_for("transparent") is None; n += 1
    assert m.colour_for("white") == (1.0, 1.0, 1.0); n += 1
    assert m.colour_for("black") == (0.0, 0.0, 0.0); n += 1
    assert m.colour_for("grey") == (0.5, 0.5, 0.5); n += 1
    assert m.colour_for("green screen") == (0.0, 1.0, 0.0); n += 1
    assert "background must be" in refuses(m.colour_for, "pink"); n += 1
    for name in m.BACKGROUNDS:
        assert name == "transparent" or len(m.colour_for(name)) == 3
    n += 1
    # ---- blend_over
    assert m.blend_over((1.0, 0.0, 0.0), 1.0, (0.0, 1.0, 0.0)) == (1.0, 0.0, 0.0); n += 1
    assert m.blend_over((1.0, 0.0, 0.0), 0.0, (0.0, 1.0, 0.0)) == (0.0, 1.0, 0.0); n += 1
    r = m.blend_over((1.0, 0.0, 0.0), 0.25, (0.0, 1.0, 0.0))
    assert close(r[0], 0.25) and close(r[1], 0.75) and close(r[2], 0.0); n += 1
    assert m.blend_over((1, 1, 1), 5.0, (0, 0, 0)) == (1.0, 1.0, 1.0); n += 1   # alpha clamped
    assert m.blend_over((1, 1, 1), -2.0, (0, 0, 0)) == (0.0, 0.0, 0.0); n += 1
    # ---- threshold_value
    assert m.threshold_value(0.3, 0.0) == 0.3; n += 1
    assert m.threshold_value(1.7, 0.0) == 1.0 and m.threshold_value(-0.2, 0.0) == 0.0; n += 1
    assert m.threshold_value(0.5, 0.5) == 1.0; n += 1
    assert m.threshold_value(0.49, 0.5) == 0.0; n += 1
    assert m.threshold_value(1.0, 1.0) == 1.0 and m.threshold_value(0.99, 1.0) == 0.0; n += 1
    assert "threshold" in refuses(m.threshold_value, 0.5, 1.5); n += 1
    assert "threshold" in refuses(m.threshold_value, 0.5, -0.1); n += 1
    # ---- names and the model list
    assert m.check_plain_name("a/b.safetensors") == "a/b.safetensors"; n += 1
    for bad in ("", "  ", None, "../x.pt", "a/../b.pt", "/etc/x", "C:/x.pt", "c:\\x.pt", "\\\\srv\\x.pt"):
        assert refuses(m.check_plain_name, bad) is not None, bad
    n += 1
    assert m.model_choices([]) == [m.NO_MODEL]; n += 1
    assert m.model_choices(["b.pt", "a.pt", "", None]) == ["a.pt", "b.pt"]; n += 1
    assert m.NO_MODEL.startswith("(no model installed") and "Model Downloader SY" in m.NO_MODEL; n += 1
    msg = refuses(m.resolve_model_path, m.NO_MODEL)
    assert msg and "models/background_removal" in msg; n += 1
    assert refuses(m.resolve_model_path, "../evil.pt") is not None; n += 1
    # ---- node shape
    c = m.SYRemoveBackground
    assert c.RETURN_TYPES == ("IMAGE", "MASK", "IMAGE") and c.RETURN_NAMES == ("image", "mask", "cutout"); n += 1
    assert m.NODE_CLASS_MAPPINGS["SYRemoveBackground"] is c; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYRemoveBackground"] == "Remove Background SY"; n += 1
    assert c.CATEGORY == "SY/Image"; n += 1
    spec = c.INPUT_TYPES()
    assert list(spec["required"]) == ["image", "model", "threshold", "feather", "grow", "background"]; n += 1
    assert spec["required"]["model"][0] == m.list_models() and spec["required"]["background"][0] == list(m.BACKGROUNDS); n += 1
    assert spec["required"]["grow"][1]["min"] == -64 and spec["required"]["feather"][1]["max"] == 64; n += 1
    for k, d in spec["required"].items():
        assert 0 < len(d[1]["tooltip"]) <= 120, k
    n += 1
    assert c.DESCRIPTION; n += 1

    # ---- torch part (only when torch is installed)
    try:
        import torch
    except ImportError:
        torch = None
    if torch is not None:
        node = c()
        H, W = 12, 16
        img = torch.rand(1, H, W, 3)
        hard = torch.zeros(1, H, W)
        hard[:, 4:8, 6:10] = 1.0          # a 4x4 square subject

        class Fake:
            def __init__(self, mask):
                self.mask = mask
                self.seen = None

            def encode_image(self, image):
                self.seen = tuple(image.shape)
                return self.mask

        fake = Fake(hard)
        saved = (m._get_model, m.resolve_model_path, m._release)
        released = []
        m._get_model = lambda path: fake
        m.resolve_model_path = lambda name: "fake.pt"
        m._release = lambda mod: released.append(mod)
        try:
            # transparent: RGBA, alpha equals the mask, colours kept
            out, mk, cut = node.run(img, "fake", 0.0, 0, 0, "transparent")
            assert out.shape == (1, H, W, 4) and mk.shape == (1, H, W) and cut.shape == (1, H, W, 3); n += 1
            assert torch.equal(out[..., 3], mk) and torch.equal(mk, hard); n += 1
            assert torch.equal(out[..., :3], img); n += 1
            assert fake.seen == (1, H, W, 3) and released == [fake]; n += 1       # model got RGB, was released after
            assert float(cut[0, 0, 0, 0]) == 0.0 and torch.equal(cut[0, 5, 7], img[0, 5, 7]); n += 1   # cutout fill black when transparent
            # solid backgrounds
            for name, col in (("white", 1.0), ("black", 0.0), ("grey", 0.5)):
                out, mk, cut = node.run(img, "fake", 0.0, 0, 0, name)
                assert out.shape == (1, H, W, 3) and torch.equal(out, cut); n += 1
                assert float(out[0, 0, 0, 0]) == col and float(out[0, 0, 0, 2]) == col and torch.equal(out[0, 5, 7], img[0, 5, 7]); n += 1
            out, mk, cut = node.run(img, "fake", 0.0, 0, 0, "green screen")
            assert [float(v) for v in out[0, 0, 0]] == [0.0, 1.0, 0.0]; n += 1
            # soft mask is kept when threshold is 0, and cut by the threshold
            soft = torch.zeros(1, H, W)
            soft[:, :, :] = 0.3
            soft[:, 4:8, 6:10] = 0.8
            fake.mask = soft
            out, mk, cut = node.run(img, "fake", 0.0, 0, 0, "transparent")
            assert close(float(mk[0, 0, 0]), 0.3) and close(float(mk[0, 5, 7]), 0.8); n += 1
            out, mk, cut = node.run(img, "fake", 0.5, 0, 0, "transparent")
            assert float(mk[0, 0, 0]) == 0.0 and float(mk[0, 5, 7]) == 1.0; n += 1
            out, mk, cut = node.run(img, "fake", 0.9, 0, 0, "transparent")
            assert float(mk.sum()) == 0.0; n += 1
            fake.mask = torch.full((1, H, W), 0.5)
            out, mk, cut = node.run(img, "fake", 0.5, 0, 0, "transparent")     # at the level counts as inside
            assert float(mk.min()) == 1.0; n += 1
            # blended cutout on a soft edge matches blend_over
            fake.mask = torch.full((1, H, W), 0.25)
            out, mk, cut = node.run(img, "fake", 0.0, 0, 0, "white")
            want = m.blend_over([float(v) for v in img[0, 1, 1]], 0.25, (1.0, 1.0, 1.0))
            assert all(close(float(out[0, 1, 1, k]), want[k]) for k in range(3)); n += 1
            # grow and shrink
            fake.mask = hard
            out, mk, cut = node.run(img, "fake", 0.0, 0, 2, "transparent")
            assert float(mk.sum()) == 8 * 8 and float(mk[0, 2, 4]) == 1.0 and float(mk[0, 1, 4]) == 0.0; n += 1
            out, mk, cut = node.run(img, "fake", 0.0, 0, -1, "transparent")
            assert float(mk.sum()) == 2 * 2 and float(mk[0, 5, 7]) == 1.0 and float(mk[0, 4, 6]) == 0.0; n += 1
            out, mk, cut = node.run(img, "fake", 0.0, 0, -2, "transparent")
            assert float(mk.sum()) == 0.0; n += 1
            fake.mask = torch.ones(1, H, W)
            out, mk, cut = node.run(img, "fake", 0.0, 0, -3, "transparent")
            assert float(mk.min()) == 1.0; n += 1                               # picture edges do not eat the subject
            # feather
            fake.mask = hard
            out, mk, cut = node.run(img, "fake", 0.0, 2, 0, "transparent")
            assert 0.0 < float(mk[0, 3, 7]) < 1.0 and float(mk.min()) >= 0.0 and float(mk.max()) <= 1.0; n += 1
            assert 0.4 < float(mk[0, 5, 7]) < 1.0; n += 1
            assert torch.equal(out[..., 3], mk); n += 1
            row = [float(mk[0, 5, x]) for x in range(0, 8)]
            assert all(row[i] <= row[i + 1] + 1e-6 for i in range(7)); n += 1    # rises into the subject
            # threshold, grow, feather together keep values in range
            fake.mask = soft
            out, mk, cut = node.run(img, "fake", 0.5, 3, 2, "black")
            assert float(mk.min()) >= 0.0 and float(mk.max()) <= 1.0 and out.shape == (1, H, W, 3); n += 1
            # batch of 3 with different masks
            imgs = torch.rand(3, H, W, 3)
            masks = torch.zeros(3, H, W)
            masks[0, :, :4] = 1.0
            masks[1, :, 8:] = 1.0
            fake.mask = masks
            out, mk, cut = node.run(imgs, "fake", 0.0, 0, 0, "transparent")
            assert out.shape == (3, H, W, 4) and mk.shape == (3, H, W); n += 1
            assert torch.equal(out[..., 3], masks) and float(mk[2].sum()) == 0.0 and float(mk[0].sum()) == 4 * H; n += 1
            assert torch.equal(out[1, :, 10, :3], imgs[1, :, 10]); n += 1
            fake.mask = hard                                                       # one mask for 3 pictures
            out, mk, cut = node.run(imgs, "fake", 0.0, 0, 0, "white")
            assert out.shape == (3, H, W, 3) and float(mk.sum()) == 3 * 16; n += 1
            # RGBA input: its alpha is ignored, output uses the model mask
            rgba = torch.rand(1, H, W, 4)
            out, mk, cut = node.run(rgba, "fake", 0.0, 0, 0, "transparent")
            assert out.shape == (1, H, W, 4) and torch.equal(out[..., :3], rgba[..., :3]) and fake.seen == (1, H, W, 3); n += 1
            # a mask of a different size is stretched to the picture
            fake.mask = torch.ones(1, 6, 8)
            out, mk, cut = node.run(img, "fake", 0.0, 0, 0, "transparent")
            assert mk.shape == (1, H, W) and close(float(mk.min()), 1.0); n += 1
            fake.mask = torch.ones(H, W)                                          # 2-D mask accepted
            out, mk, cut = node.run(img, "fake", 0.0, 0, 0, "transparent")
            assert mk.shape == (1, H, W); n += 1
            fake.mask = torch.ones(2, H, W)
            assert "2 masks for 1" in refuses(node.run, img, "fake", 0.0, 0, 0, "transparent"); n += 1
            fake.mask = hard
            # the input picture is not changed
            before = img.clone()
            node.run(img, "fake", 0.0, 3, 3, "green screen")
            assert torch.equal(img, before); n += 1
            # refusals
            assert "grow must" in refuses(node.run, img, "fake", 0.0, 0, 99, "transparent"); n += 1
            assert "feather" in refuses(node.run, img, "fake", 0.0, 99, 0, "transparent"); n += 1
            assert "threshold" in refuses(node.run, img, "fake", 2.0, 0, 0, "transparent"); n += 1
            assert "background must" in refuses(node.run, img, "fake", 0.0, 0, 0, "pink"); n += 1
            assert "picture batch" in refuses(node.run, torch.zeros(5, 5), "fake", 0.0, 0, 0, "transparent"); n += 1
            assert "picture batch" in refuses(node.run, torch.zeros(1, 4, 4, 2), "fake", 0.0, 0, 0, "transparent"); n += 1
        finally:
            m._get_model, m.resolve_model_path, m._release = saved
        # no model installed: plain refusal that names the folder
        msg = refuses(node.run, img, m.NO_MODEL)
        assert msg and "models/background_removal" in msg; n += 1
        # a missing model file name is refused (with or without ComfyUI present)
        assert refuses(node.run, img, "does-not-exist.safetensors") is not None; n += 1
    return n
