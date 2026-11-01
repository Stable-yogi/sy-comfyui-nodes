import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_paste_back as m
import sy_outpaint_pad as op


def refuses(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    # ---- parse_box
    assert m.parse_box("10,20,30,40") == (10, 20, 30, 40); n += 1
    assert m.parse_box("  10 , 20 ,30,  40 ") == (10, 20, 30, 40); n += 1
    assert m.parse_box("0,0,1,1") == (0, 0, 1, 1); n += 1
    assert m.parse_box("199,0,512,512\n") == (199, 0, 512, 512); n += 1
    assert "empty" in refuses(m.parse_box, ""); n += 1
    assert "empty" in refuses(m.parse_box, "   "); n += 1
    assert "empty" in refuses(m.parse_box, None); n += 1
    assert "four numbers" in refuses(m.parse_box, "1,2,3"); n += 1
    assert "four numbers" in refuses(m.parse_box, "1,2,3,4,5"); n += 1
    assert "whole number" in refuses(m.parse_box, "a,2,3,4") and "x must" in refuses(m.parse_box, "a,2,3,4"); n += 1
    assert "height must be a whole" in refuses(m.parse_box, "1,2,3,x"); n += 1
    assert "whole number" in refuses(m.parse_box, "1.5,2,3,4"); n += 1
    assert "negative" in refuses(m.parse_box, "-1,0,3,4"); n += 1
    assert "negative" in refuses(m.parse_box, "0,-5,3,4"); n += 1
    assert "at least 1" in refuses(m.parse_box, "0,0,0,4"); n += 1
    assert "at least 1" in refuses(m.parse_box, "0,0,4,0"); n += 1
    assert "at least 1" in refuses(m.parse_box, "0,0,-4,4"); n += 1
    # ---- check_box
    assert m.check_box((10, 4, 30, 20), 46, 24) == (10, 4, 30, 20); n += 1
    assert m.check_box((0, 0, 5, 5), 5, 5) == (0, 0, 5, 5); n += 1
    msg = refuses(m.check_box, (10, 4, 40, 20), 46, 24, "image")
    assert msg and "40x20" in msg and "46x24" in msg and "image" in msg; n += 1
    msg = refuses(m.check_box, (0, 10, 5, 20), 50, 24, "target picture")
    assert msg and "target picture" in msg and "50x24" in msg; n += 1
    assert refuses(m.check_box, (1, 0, 5, 5), 5, 5) is not None; n += 1
    # ---- feather profile
    assert m.feather_profile(5, 0) == [1.0] * 5; n += 1
    assert m.feather_profile(0, 4) == []; n += 1
    f = m.feather_profile(20, 4)
    assert f == f[::-1] and f[0] < f[1] < f[2] < f[3] < 1.0 and f[4] == 1.0 and f[10] == 1.0; n += 1
    assert 0.0 < f[0] < 0.2; n += 1
    assert all(0.0 <= v <= 1.0 for v in m.feather_profile(7, 256)); n += 1
    f = m.feather_profile(3, 10)
    assert f[1] > f[0] and f == f[::-1]; n += 1
    assert m.feather_profile(1, 5)[0] > 0.0; n += 1
    # ---- text helpers
    assert m.batch_plan(2, 2) == 2 and m.batch_plan(3, 1) == 3 and m.batch_plan(1, 1) == 1; n += 1
    msg = refuses(m.batch_plan, 3, 2)
    assert msg and "3" in msg and "2" in msg; n += 1
    assert refuses(m.batch_plan, 1, 2) is not None; n += 1
    ci = m.cut_info((10, 4, 30, 20), 46, 24, 2)
    assert "30x20" in ci and "46x24" in ci and "10,4" in ci and "2 pictures" in ci; n += 1
    pi = m.paste_info((10, 4, 30, 20), 100, 80, 1, 0, False)
    assert "hard edge" in pi and "100x80" in pi and "1 picture)" in pi; n += 1
    pi = m.paste_info((10, 4, 30, 20), 100, 80, 1, 8, True)
    assert "edge feather 8 px" in pi and "soft mask" in pi; n += 1
    # ---- node shape
    c = m.SYPasteBackBox
    assert c.RETURN_NAMES == ("image", "info") and c.RETURN_TYPES == ("IMAGE", "STRING"); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYPasteBackBox"] == "Paste Back Box SY"; n += 1
    assert m.NODE_CLASS_MAPPINGS["SYPasteBackBox"] is c; n += 1
    spec = c.INPUT_TYPES()
    assert list(spec["required"]) == ["image", "crop_box", "mode"] and list(spec["optional"]) == ["target", "mask", "feather"]; n += 1
    assert spec["required"]["crop_box"][1]["forceInput"] is True; n += 1
    assert spec["required"]["mode"][0] == list(m.MODES) and spec["optional"]["feather"][1]["max"] == 256; n += 1
    for sect in ("required", "optional"):
        for k, d in spec[sect].items():
            assert 0 < len(d[1]["tooltip"]) <= 120, k
    n += 1
    assert "SAME x,y" in c.DESCRIPTION; n += 1
    assert c.CATEGORY.startswith("SY/"); n += 1

    # ---- torch part (only when torch is installed)
    try:
        import torch
    except ImportError:
        torch = None
    if torch is not None:
        node = c()
        CUT, PASTE = m.MODES
        img = torch.rand(2, 24, 46, 3)
        out, info = node.run(img, "10,4,30,20", CUT)
        assert out.shape == (2, 20, 30, 3) and torch.equal(out, img[:, 4:24, 10:40]) and "cut 30x20" in info; n += 1
        out, _ = node.run(img, " 0 , 0 , 46 , 24 ", CUT)
        assert torch.equal(out, img); n += 1
        # cut out ignores target, mask, feather
        out, _ = node.run(img, "1,1,2,2", CUT, torch.zeros(1, 5, 5, 3), torch.zeros(1, 24, 46), 9)
        assert torch.equal(out, img[:, 1:3, 1:3]); n += 1
        # ---- round trip with Outpaint Pad SY: pad, cut out with its crop_box, get the original back
        orig = torch.rand(2, 20, 30, 3)
        for fill in op.FILLS:
            padded, _, _, box = op.SYOutpaintPad().run(orig, 10, 4, 6, 3, "off", 8, fill)
            back, _ = node.run(padded, box, CUT)
            assert torch.equal(back, orig), fill
            n += 1
        padded, _, _, box = op.SYOutpaintPad().run(orig, 0, 0, 0, 0, "off", 1)
        assert torch.equal(node.run(padded, box, CUT)[0], orig); n += 1
        padded, _, _, box = op.SYOutpaintPad().run(orig, 0, 0, 0, 0, "16:9", 8)
        assert torch.equal(node.run(padded, box, CUT)[0], orig); n += 1
        rgba = torch.rand(1, 10, 10, 4)
        padded, _, _, box = op.SYOutpaintPad().run(rgba, 4, 4, 4, 4, "off", 1, "mirror")
        assert torch.equal(node.run(padded, box, CUT)[0], rgba); n += 1
        # ---- paste: hard
        tgt = torch.zeros(1, 40, 60, 3)
        edit = torch.ones(1, 24, 46, 3)
        out, info = node.run(edit, "10,4,30,20", PASTE, tgt)
        assert out.shape == (1, 40, 60, 3) and "hard edge" in info; n += 1
        assert float(out[0, 4:24, 10:40].min()) == 1.0 and float(out.sum()) == 20 * 30 * 3; n += 1  # only the box changed
        assert float(out[0, 3, 10, 0]) == 0.0 and float(out[0, 24, 10, 0]) == 0.0 and float(out[0, 4, 9, 0]) == 0.0 and float(out[0, 4, 40, 0]) == 0.0; n += 1
        assert float(tgt.sum()) == 0.0; n += 1  # the target is not changed in place
        # same x,y: content comes from the same place in image
        edit2 = torch.rand(1, 24, 46, 3)
        out, _ = node.run(edit2, "10,4,30,20", PASTE, tgt)
        assert torch.equal(out[:, 4:24, 10:40], edit2[:, 4:24, 10:40]); n += 1
        # paste back what was cut out: original returns inside the target
        padded, _, _, box = op.SYOutpaintPad().run(orig[:1], 10, 4, 6, 3, "off", 8, "grey")
        big = torch.rand(1, 40, 60, 3)
        out, _ = node.run(padded, box, PASTE, big)
        assert torch.equal(out[:, 4:24, 10:40], orig[:1]) and torch.equal(out[:, :4], big[:, :4]); n += 1
        # ---- paste: batch
        out, info = node.run(torch.ones(3, 24, 46, 3), "10,4,30,20", PASTE, tgt)
        assert out.shape == (3, 40, 60, 3) and "3 pictures" in info; n += 1
        out, _ = node.run(torch.ones(2, 24, 46, 3), "10,4,30,20", PASTE, torch.zeros(2, 40, 60, 3))
        assert out.shape[0] == 2; n += 1
        assert "target batch has 2" in refuses(node.run, torch.ones(3, 24, 46, 3), "10,4,30,20", PASTE, torch.zeros(2, 40, 60, 3)); n += 1
        assert refuses(node.run, torch.ones(1, 24, 46, 3), "10,4,30,20", PASTE, torch.zeros(2, 40, 60, 3)) is not None; n += 1
        # ---- paste: mask
        mask = torch.zeros(1, 24, 46)
        mask[:, :, 25:] = 1.0
        out, info = node.run(edit, "10,4,30,20", PASTE, tgt, mask)
        assert "soft mask" in info; n += 1
        assert float(out[0, 10, 24, 0]) == 0.0 and float(out[0, 10, 25, 0]) == 1.0 and float(out[0, 10, 39, 0]) == 1.0 and float(out[0, 10, 12, 0]) == 0.0; n += 1
        half = torch.full((1, 24, 46), 0.5)
        tg1 = torch.ones(1, 40, 60, 3)
        out, _ = node.run(torch.zeros(1, 24, 46, 3), "10,4,30,20", PASTE, tg1, half)
        assert abs(float(out[0, 10, 20, 0]) - 0.5) < 1e-6 and float(out[0, 0, 0, 0]) == 1.0; n += 1
        # mask the size of the box, 2-D mask, mask batch of 1 against 3 pictures
        out, _ = node.run(torch.zeros(1, 24, 46, 3), "10,4,30,20", PASTE, tg1, torch.full((20, 30), 0.5))
        assert abs(float(out[0, 10, 20, 0]) - 0.5) < 1e-6; n += 1
        out, _ = node.run(torch.zeros(1, 24, 46, 3), "10,4,30,20", PASTE, tg1, torch.full((1, 20, 30), 0.25))
        assert abs(float(out[0, 10, 20, 0]) - 0.75) < 1e-6; n += 1
        out, _ = node.run(torch.zeros(3, 24, 46, 3), "10,4,30,20", PASTE, tg1, half)
        assert out.shape[0] == 3; n += 1
        assert "must match the image" in refuses(node.run, edit, "10,4,30,20", PASTE, tgt, torch.zeros(1, 7, 7)); n += 1
        assert "mask batch" in refuses(node.run, torch.ones(3, 24, 46, 3), "10,4,30,20", PASTE, tgt, torch.zeros(2, 24, 46)); n += 1
        assert "mask must be" in refuses(node.run, edit, "10,4,30,20", PASTE, tgt, torch.zeros(24, 46, 1, 1)); n += 1
        # ---- paste: feather
        out, info = node.run(torch.zeros(1, 24, 46, 3), "10,4,30,20", PASTE, tg1, None, 6)
        assert "edge feather 6" in info; n += 1
        assert float(out[0, 14, 25, 0]) == 0.0 and 0.0 < float(out[0, 4, 25, 0]) < 1.0; n += 1  # middle fully pasted, edge soft
        assert float(out[0, 3, 25, 0]) == 1.0 and float(out[0, 14, 9, 0]) == 1.0; n += 1  # outside the box untouched
        row = [float(out[0, 14, 10 + i, 0]) for i in range(7)]
        assert all(row[i] >= row[i + 1] for i in range(6)) and row[0] > 0.7 and row[6] == 0.0; n += 1
        out2, _ = node.run(torch.zeros(1, 24, 46, 3), "10,4,30,20", PASTE, tg1, half, 6)
        assert abs(float(out2[0, 14, 25, 0]) - 0.5) < 1e-6 and float(out2[0, 14, 10, 0]) > float(out[0, 14, 10, 0]); n += 1  # mask and feather multiply
        # ---- RGBA kept
        rgba_t = torch.rand(1, 40, 60, 4)
        rgba_e = torch.rand(1, 24, 46, 4)
        out, _ = node.run(rgba_e, "10,4,30,20", PASTE, rgba_t)
        assert out.shape[-1] == 4 and torch.equal(out[:, 4:24, 10:40], rgba_e[:, 4:24, 10:40]); n += 1
        out, _ = node.run(edit, "10,4,30,20", PASTE, rgba_t)
        assert out.shape[-1] == 4 and float(out[0, 10, 20, 3]) == 1.0 and float(out[0, 10, 20, 0]) == 1.0; n += 1
        out, _ = node.run(rgba_e, "10,4,30,20", PASTE, tgt)
        assert out.shape[-1] == 3 and torch.equal(out[:, 4:24, 10:40], rgba_e[:, 4:24, 10:40, :3]); n += 1
        # ---- refusals through the node
        assert "needs a target" in refuses(node.run, edit, "10,4,30,20", PASTE); n += 1
        msg = refuses(node.run, edit, "10,4,40,20", CUT)
        assert msg and "46x24" in msg and "40x20" in msg; n += 1
        msg = refuses(node.run, edit, "10,4,30,20", PASTE, torch.zeros(1, 10, 10, 3))
        assert msg and "target picture" in msg and "10x10" in msg; n += 1
        assert "crop_box" in refuses(node.run, edit, "nonsense", CUT); n += 1
        assert "mode must" in refuses(node.run, edit, "0,0,2,2", "swap"); n += 1
        assert "feather must" in refuses(node.run, edit, "0,0,2,2", PASTE, tgt, None, 300); n += 1
        assert "expected a picture" in refuses(node.run, torch.zeros(5, 5), "0,0,2,2", CUT); n += 1
        assert "expected a picture" in refuses(node.run, edit, "0,0,2,2", PASTE, torch.zeros(5, 5)); n += 1
        assert "empty" in refuses(node.run, torch.zeros(0, 4, 4, 3), "0,0,2,2", CUT); n += 1
    return n
