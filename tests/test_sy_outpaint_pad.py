import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_outpaint_pad as m


def refuses(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    # ---- plan_padding: plain numbers
    assert m.plan_padding(512, 512, 0, 0, 0, 0, "off", 8) == (0, 0, 0, 0, 512, 512); n += 1
    assert m.plan_padding(512, 512, 100, 0, 100, 0, "off", 1) == (100, 0, 100, 0, 712, 512); n += 1
    assert m.plan_padding(512, 512, 100, 0, 0, 0, "off", 8) == (100, 0, 4, 0, 616, 512); n += 1  # 612 -> 616, extra on the right
    assert m.plan_padding(513, 511, 0, 0, 0, 0, "off", 8) == (0, 0, 7, 1, 520, 512); n += 1
    assert m.plan_padding(100, 100, 3, 5, 7, 9, "off", 16)[4:] == (112, 128); n += 1
    assert m.plan_padding(100, 100, 0, 0, 0, 0, "off", 1) == (0, 0, 0, 0, 100, 100); n += 1
    # multiple never changes the left/top
    p = m.plan_padding(300, 200, 11, 13, 0, 0, "off", 64)
    assert p[0] == 11 and p[1] == 13 and p[4] % 64 == 0 and p[5] % 64 == 0; n += 1
    # ---- plan_padding: aspect overrides the numbers
    p = m.plan_padding(512, 512, 999, 999, 999, 999, "16:9", 1)
    assert p == (199, 0, 200, 0, 911, 512); n += 1
    p = m.plan_padding(512, 512, 0, 0, 0, 0, "16:9", 8)
    assert p[4] == 912 and p[5] == 512 and p[0] == 199 and p[2] == 201; n += 1
    p = m.plan_padding(1024, 512, 0, 0, 0, 0, "1:1", 1)
    assert p == (0, 256, 0, 256, 1024, 1024); n += 1
    p = m.plan_padding(1024, 512, 5, 5, 5, 5, "9:16", 1)
    assert p[4] == 1024 and p[5] == 1821 and p[0] == 0 and p[2] == 0; n += 1
    assert m.plan_padding(1600, 900, 7, 7, 7, 7, "16:9", 1) == (0, 0, 0, 0, 1600, 900); n += 1  # already that shape
    for asp in m.ASPECTS[1:]:
        a, b = (int(v) for v in asp.split(":"))
        q = m.plan_padding(640, 480, 0, 0, 0, 0, asp, 1)
        assert abs(q[4] * b - q[5] * a) < max(a, b); n += 1
    # centring: left and right differ by at most 1
    q = m.plan_padding(333, 777, 0, 0, 0, 0, "21:9", 1)
    assert abs(q[0] - q[2]) <= 1 and q[1] == q[3] == 0; n += 1
    # ---- plan_padding: refusals
    assert "to_aspect" in refuses(m.plan_padding, 10, 10, 0, 0, 0, 0, "5:7", 8); n += 1
    assert "multiple" in refuses(m.plan_padding, 10, 10, 0, 0, 0, 0, "off", 0); n += 1
    assert "multiple" in refuses(m.plan_padding, 10, 10, 0, 0, 0, 0, "off", 513); n += 1
    assert "left must be" in refuses(m.plan_padding, 10, 10, -1, 0, 0, 0, "off", 8); n += 1
    assert "bottom must be" in refuses(m.plan_padding, 10, 10, 0, 0, 0, 9000, "off", 8); n += 1
    msg = refuses(m.plan_padding, 12000, 100, 4000, 0, 4000, 0, "off", 8)
    assert msg and "20000x104" in msg and "16384" in msg; n += 1
    msg = refuses(m.plan_padding, 9000, 9000, 3000, 0, 0, 0, "off", 8)
    assert msg and "megapixels" in msg and "12000x9000" in msg; n += 1
    assert refuses(m.plan_padding, 8000, 8000, 0, 0, 0, 0, "off", 8) is None; n += 1  # 64 MP is fine
    assert refuses(m.plan_padding, 10000, 10000, 1, 0, 0, 0, "off", 8) is not None; n += 1  # 100.0x MP
    assert "at least" in refuses(m.plan_padding, 0, 10, 0, 0, 0, 0, "off", 8); n += 1
    # ---- index maths
    assert m.edge_index(8, 3, 4) == [0, 0, 0, 0, 1, 2, 3, 3]; n += 1
    assert m.mirror_index(8, 3, 4) == [2, 1, 0, 0, 1, 2, 3, 3]; n += 1
    assert m.mirror_index(10, 5, 2) == [0, 0, 1, 1, 0, 0, 1, 1, 0, 0]; n += 1  # margin bigger than picture
    assert m.mirror_index(3, 0, 1) == [0, 0, 0]; n += 1
    assert m.mirror_index(6, 0, 6) == [0, 1, 2, 3, 4, 5]; n += 1
    # ---- feather profile
    f = m.feather_profile(10, 0, 0, True, False)
    assert f == [0.0] * 10; n += 1
    f = m.feather_profile(10, 2, 0, True, False)
    assert f[:2] == [1.0, 1.0] and f[2:] == [0.0] * 8; n += 1
    f = m.feather_profile(20, 0, 8, True, False)
    assert 0.0 < f[0] < 1.0 and f[8] == 0.0 and f[7] > 0.0 and f[19] == 0.0; n += 1
    assert all(f[i] >= f[i + 1] for i in range(19)); n += 1
    f = m.feather_profile(40, 4, 8, True, True)
    assert f[0] == f[39] == 1.0 and f[3] == 1.0 and f[4] < 1.0 and f[20] == 0.0 and f == f[::-1]; n += 1
    f = m.feather_profile(10, 3, 4, False, False)
    assert f == [0.0] * 10; n += 1  # no padding on that side, no seam
    assert m.feather_profile(1, 0, 5, True, True)[0] > 0.0; n += 1
    # ---- text helpers
    assert m.crop_box_text(1, 2, 3, 4) == "1,2,3,4"; n += 1
    info = m.pad_info(512, 512, (100, 0, 100, 0, 712, 512), "off", "mirror", 16, 4, 8)
    for need in ("512x512 -> 712x512", "left 100", "right 100", "mirror", "feather 16", "grow 4", "multiple of 8"):
        assert need in info, need
        n += 1
    assert "nothing to add" in m.pad_info(64, 64, (0, 0, 0, 0, 64, 64), "off", "grey", 0, 0, 8); n += 1
    assert "centred to 16:9" in m.pad_info(512, 512, (199, 0, 201, 0, 912, 512), "16:9", "grey", 0, 0, 1); n += 1
    assert "most of the picture" in m.pad_info(20, 20, (5, 0, 0, 0, 25, 20), "off", "grey", 30, 0, 1); n += 1
    # ---- node shape
    c = m.SYOutpaintPad
    assert c.RETURN_NAMES == ("image", "mask", "info", "crop_box") and len(c.RETURN_TYPES) == 4; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYOutpaintPad"] == "Outpaint Pad SY"; n += 1
    spec = c.INPUT_TYPES()
    assert list(spec["required"]) == ["image", "left", "top", "right", "bottom"]; n += 1
    assert spec["optional"]["fill"][0] == list(m.FILLS) and spec["optional"]["to_aspect"][0] == list(m.ASPECTS); n += 1

    # ---- torch part (only when torch is installed)
    try:
        import torch
    except ImportError:
        torch = None
    if torch is not None:
        node = c()
        img = torch.rand(2, 20, 30, 3)
        out, mask, info, box = node.run(img, 10, 4, 6, 0, "off", 1, "edge stretch", 0, 0)
        assert out.shape == (2, 24, 46, 3) and mask.shape == (2, 24, 46) and box == "10,4,30,20"; n += 1
        assert torch.equal(out[:, 4:24, 10:40], img); n += 1                         # the original is untouched
        assert float(mask[:, 4:24, 10:40].max()) == 0.0 and float(mask.sum()) == 2 * (24 * 46 - 20 * 30); n += 1
        assert torch.equal(out[:, 0, 12], out[:, 4, 12]) and torch.equal(out[:, 10, 0], out[:, 10, 10]); n += 1  # edge stretch
        assert torch.equal(out[:, 10, 45], out[:, 10, 39]); n += 1
        # mirror
        out, mask, _, _ = node.run(img, 10, 0, 0, 0, "off", 1, "mirror")
        assert torch.equal(out[:, :, 9], img[:, :, 0]) and torch.equal(out[:, :, 8], img[:, :, 1]) and torch.equal(out[:, :, 10:], img); n += 1
        out, _, _, _ = node.run(img, 70, 0, 0, 0, "off", 1, "mirror")  # margin bigger than the picture
        assert out.shape[2] == 100 and torch.equal(out[:, :, 70:], img) and torch.equal(out[:, :, 69], img[:, :, 0]); n += 1
        # grey and black
        out, _, _, _ = node.run(img, 0, 0, 5, 5, "off", 1, "grey")
        assert float(out[0, 0, 30:, :].min()) == 0.5 and float(out[0, 0, 30:, :].max()) == 0.5 and float(out[0, 22, 5, 0]) == 0.5; n += 1
        out, _, _, _ = node.run(img, 0, 0, 5, 5, "off", 1, "black")
        assert float(out[:, :, 30:].abs().max()) == 0.0; n += 1
        # blur of picture: smooth, same size, original kept, values in range
        out, mask, _, _ = node.run(img, 40, 40, 40, 40, "off", 1, "blur of picture")
        assert out.shape == (2, 100, 110, 3) and torch.equal(out[:, 40:60, 40:70], img); n += 1
        assert 0.0 <= float(out.min()) and float(out.max()) <= 1.0; n += 1
        assert float((out[:, 0, 1:, :] - out[:, 0, :-1, :]).abs().max()) < 0.2; n += 1
        # aspect + multiple through the node
        out, mask, info, box = node.run(torch.zeros(1, 512, 512, 3), 0, 0, 0, 0, "16:9", 8)
        assert out.shape == (1, 512, 912, 3) and mask.shape == (1, 512, 912) and box == "199,0,512,512"; n += 1
        assert "512x512 -> 912x512" in info; n += 1
        # feather: soft values only inside the picture, only next to padded sides
        out, mask, _, _ = node.run(img, 10, 0, 0, 0, "off", 1, "grey", 8, 0)
        assert float(mask[0, :, :10].min()) == 1.0; n += 1
        assert 0.0 < float(mask[0, 5, 10]) < 1.0 and float(mask[0, 5, 18]) == 0.0 and float(mask[0, 5, 17]) > 0.0; n += 1
        assert float(mask[0, 0, 25]) == 0.0 and float(mask[0, 19, 25]) == 0.0; n += 1  # top/bottom were not padded
        # grow is a hard band into the picture
        _, mask, _, _ = node.run(img, 10, 0, 0, 0, "off", 1, "grey", 0, 3)
        assert float(mask[0, 5, 12]) == 1.0 and float(mask[0, 5, 13]) == 0.0; n += 1
        # batch: same mask for every image
        assert torch.equal(mask[0], mask[1]); n += 1
        # nothing to add
        out, mask, info, box = node.run(torch.rand(1, 16, 16, 3), 0, 0, 0, 0, "off", 8)
        assert out.shape == (1, 16, 16, 3) and float(mask.max()) == 0.0 and "nothing to add" in info and box == "0,0,16,16"; n += 1
        # RGBA keeps alpha, new area opaque
        rgba = torch.rand(1, 10, 10, 4)
        rgba[..., 3] = 0.25
        for fl in m.FILLS:
            out, _, _, _ = node.run(rgba, 4, 4, 4, 4, "off", 1, fl)
            assert out.shape == (1, 18, 18, 4) and float(out[0, 0, 0, 3]) == 1.0 and float(out[0, 9, 9, 3]) == 0.25; n += 1
        # refusals through the node
        assert "megapixels" in refuses(node.run, torch.zeros(1, 10, 10, 3), 8192, 8192, 8192, 8192); n += 1
        assert "fill must" in refuses(node.run, img, 1, 0, 0, 0, "off", 8, "paint"); n += 1
        assert "between 0 and 256" in refuses(node.run, img, 1, 0, 0, 0, "off", 8, "grey", 300, 0); n += 1
        assert "expected a picture" in refuses(node.run, torch.zeros(5, 5), 1, 0, 0, 0); n += 1
    return n
