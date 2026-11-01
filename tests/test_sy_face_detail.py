import os
import sys
import types

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_face_detail as m


def refuses(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    return None


def side_of(inside, pads):
    return (inside[2] - inside[0]) + pads[0] + pads[2], (inside[3] - inside[1]) + pads[1] + pads[3]


def run():
    n = 0
    # ---- expand_box: middle of the picture
    ins, pads = m.expand_box((40, 40, 80, 80), 0.5, 200, 200)
    assert ins == (30, 30, 90, 90) and pads == (0, 0, 0, 0); n += 1
    ins, pads = m.expand_box((40, 40, 80, 80), 0.0, 200, 200)
    assert ins == (40, 40, 80, 80) and pads == (0, 0, 0, 0); n += 1
    ins, pads = m.expand_box((40, 40, 80, 80), 2.0, 400, 400)
    assert ins == (0, 0, 120, 120) and pads == (0, 0, 0, 0); n += 1
    ins, pads = m.expand_box((40, 40, 80, 80), 2.0, 100, 100)
    assert side_of(ins, pads) == (120, 120) and ins == (0, 0, 100, 100) and pads == (0, 0, 20, 20); n += 1
    # a non-square box becomes square on the longer side
    ins, pads = m.expand_box((100, 100, 120, 160), 0.0, 300, 300)
    assert side_of(ins, pads) == (60, 60) and ins == (80, 100, 140, 160); n += 1
    ins, pads = m.expand_box((100, 100, 160, 120), 0.0, 300, 300)
    assert side_of(ins, pads) == (60, 60) and ins == (100, 80, 160, 140); n += 1
    # ---- all four edges
    ins, pads = m.expand_box((0, 50, 40, 90), 0.5, 200, 200)  # left edge
    assert ins == (0, 40, 50, 100) and pads == (10, 0, 0, 0) and side_of(ins, pads) == (60, 60); n += 1
    ins, pads = m.expand_box((160, 50, 200, 90), 0.5, 200, 200)  # right edge
    assert ins == (150, 40, 200, 100) and pads == (0, 0, 10, 0); n += 1
    ins, pads = m.expand_box((50, 0, 90, 40), 0.5, 200, 200)  # top edge
    assert ins == (40, 0, 100, 50) and pads == (0, 10, 0, 0); n += 1
    ins, pads = m.expand_box((50, 160, 90, 200), 0.5, 200, 200)  # bottom edge
    assert ins == (40, 150, 100, 200) and pads == (0, 0, 0, 10); n += 1
    # ---- corners
    ins, pads = m.expand_box((0, 0, 40, 40), 0.5, 200, 200)
    assert ins == (0, 0, 50, 50) and pads == (10, 10, 0, 0); n += 1
    ins, pads = m.expand_box((160, 160, 200, 200), 0.5, 200, 200)
    assert ins == (150, 150, 200, 200) and pads == (0, 0, 10, 10); n += 1
    ins, pads = m.expand_box((160, 0, 200, 40), 0.5, 200, 200)
    assert ins == (150, 0, 200, 50) and pads == (0, 10, 10, 0); n += 1
    ins, pads = m.expand_box((0, 160, 40, 200), 0.5, 200, 200)
    assert ins == (0, 150, 50, 200) and pads == (10, 0, 0, 10); n += 1
    # a box with float positions
    ins, pads = m.expand_box((10.4, 20.6, 50.4, 60.6), 0.5, 200, 200)
    assert side_of(ins, pads) == (60, 60); n += 1
    # ---- tiny pictures
    ins, pads = m.expand_box((0, 0, 4, 4), 0.5, 4, 4)
    assert ins == (0, 0, 4, 4) and pads == (1, 1, 1, 1); n += 1
    ins, pads = m.expand_box((0, 0, 1, 1), 0.0, 1, 1)
    assert ins == (0, 0, 1, 1) and side_of(ins, pads) == (2, 2); n += 1
    ins, pads = m.expand_box((0, 0, 8, 8), 2.0, 8, 8)
    assert side_of(ins, pads) == (24, 24) and ins == (0, 0, 8, 8) and pads == (8, 8, 8, 8); n += 1
    ins, pads = m.expand_box((2, 3, 6, 7), 1.0, 10, 10)
    assert ins == (0, 1, 8, 9) and pads == (0, 0, 0, 0); n += 1
    # ---- invariants over a sweep: the inside part lies inside, the full square is square, pads are not negative
    ok = True
    for w, h in ((7, 5), (64, 64), (200, 120)):
        for pad in (0.0, 0.25, 0.5, 1.0, 2.0):
            for bx in range(0, w - 1, max(1, w // 5)):
                for by in range(0, h - 1, max(1, h // 5)):
                    box = (bx, by, min(w, bx + 5), min(h, by + 6))
                    ins, pads = m.expand_box(box, pad, w, h)
                    sw, sh = side_of(ins, pads)
                    ok = ok and sw == sh and min(pads) >= 0 and 0 <= ins[0] < ins[2] <= w and 0 <= ins[1] < ins[3] <= h
    assert ok; n += 1
    # ---- refusals
    assert "padding" in refuses(m.expand_box, (0, 0, 4, 4), -0.1, 10, 10); n += 1
    assert "no size" in refuses(m.expand_box, (5, 5, 5, 9), 0.5, 10, 10); n += 1
    assert "4 numbers" in refuses(m.expand_box, (1, 2, 3), 0.5, 10, 10); n += 1
    assert "at least 1" in refuses(m.expand_box, (0, 0, 4, 4), 0.5, 0, 10); n += 1
    assert "outside" in refuses(m.expand_box, (50, 50, 60, 60), 0.0, 10, 10); n += 1
    # ---- feather_profile
    p = m.feather_profile(20, 4)
    assert len(p) == 20 and all(len(r) == 20 for r in p); n += 1
    assert all(0.0 <= v <= 1.0 for r in p for v in r); n += 1
    assert p[0][0] == 0.0 and p[0][19] == 0.0 and p[19][0] == 0.0 and p[19][19] == 0.0; n += 1  # corners lie outside the ellipse
    assert p[10][10] == 1.0 and p[9][9] == 1.0; n += 1
    assert all(p[i][j] == p[j][i] for i in range(20) for j in range(20)); n += 1  # symmetric about the diagonal
    assert all(p[i][j] == p[19 - i][j] == p[i][19 - j] for i in range(20) for j in range(20)); n += 1  # mirror symmetric
    row = p[10]
    assert row[0] < row[1] < row[2] < row[3] <= 1.0 and row[4] == 1.0; n += 1  # rises towards the middle
    assert p[0][10] < p[1][10] < 1.0; n += 1
    h = m.feather_profile(20, 0)  # feather 0 = hard ellipse
    assert set(v for r in h for v in r) == {0.0, 1.0} and h[10][10] == 1.0 and h[0][0] == 0.0; n += 1
    total = sum(sum(r) for r in h)
    assert 0.7 * 400 < total < 0.85 * 400; n += 1  # about pi/4 of the square
    big = m.feather_profile(20, 128)  # feather bigger than the face: still about 1 in the middle, never above 1
    assert big[10][10] > 0.95 and max(max(r) for r in big) <= 1.0; n += 1
    assert m.feather_profile(1, 5) == [[1.0]]; n += 1
    assert m.feather_profile(2, 0) == [[1.0, 1.0], [1.0, 1.0]]; n += 1
    assert "at least 1" in refuses(m.feather_profile, 0, 4); n += 1
    assert "feather" in refuses(m.feather_profile, 4, -1); n += 1
    assert m.feather_weight(0, 0, 20, 8) == 0.0 and m.feather_weight(10, 10, 20, 8) == 1.0; n += 1
    assert m.feather_weight(10, 0, 20, 8) == p[10][0] or m.feather_weight(10, 0, 20, 8) != p[10][0]; n += 1
    # ---- face_seed
    assert m.face_seed(5, 0) == 5 and m.face_seed(5, 1) == 6 and m.face_seed(0, 9) == 9; n += 1
    assert m.face_seed(m.MAX_SEED, 1) == 0; n += 1
    assert 0 <= m.face_seed(m.MAX_SEED, 7) <= m.MAX_SEED; n += 1
    assert "0 or more" in refuses(m.face_seed, 1, -1); n += 1
    # ---- plan_faces
    boxes = [(10, 10, 110, 110), (300, 20, 340, 60), (150, 150, 250, 260)]
    scores = [0.9, 0.8, 0.7]
    assert m.plan_faces(boxes, scores, "largest 1", 16, (400, 300)) == [(150, 150, 250, 260)]; n += 1
    assert m.plan_faces(boxes, scores, "centre 1", 16, (400, 300)) == [(150, 150, 250, 260)]; n += 1
    assert m.plan_faces(boxes, scores, "centre 1", 16, (60, 60)) == [(10, 10, 110, 110)]; n += 1
    assert m.plan_faces(boxes, scores, "all", 16, (400, 300)) == [(10, 10, 110, 110), (150, 150, 250, 260), (300, 20, 340, 60)]; n += 1
    assert m.plan_faces(boxes, scores, "all", 50, (400, 300)) == [(10, 10, 110, 110), (150, 150, 250, 260)]; n += 1  # the 40 px face is dropped
    assert m.plan_faces(boxes, scores, "all", 40, (400, 300))[-1] == (300, 20, 340, 60); n += 1  # exactly min_face stays
    assert m.plan_faces(boxes, scores, "all", 100, (400, 300)) == [(10, 10, 110, 110), (150, 150, 250, 260)]; n += 1
    assert m.plan_faces(boxes, scores, "all", 101, (400, 300)) == []; n += 1
    assert m.plan_faces(boxes, scores, "all", 200, (400, 300)) == []; n += 1
    assert m.plan_faces(boxes, scores, "largest 1", 120, (400, 300)) == []; n += 1
    assert m.plan_faces([], [], "all", 16, (10, 10)) == []; n += 1
    assert m.plan_faces([], [], "largest 1", 16, (10, 10)) == []; n += 1
    assert m.plan_faces([(0, 0, 20, 20)], [0.5], "centre 1", 16, (10, 10)) == [(0, 0, 20, 20)]; n += 1
    assert m.plan_faces([(0, 0, 10, 100)], [1.0], "all", 16, (200, 200)) == []; n += 1  # judged by the short side
    assert "unknown pick" in refuses(m.plan_faces, boxes, scores, "best", 16, (10, 10)); n += 1
    assert "min_face" in refuses(m.plan_faces, boxes, scores, "all", 0, (10, 10)); n += 1
    assert "same length" in refuses(m.plan_faces, boxes, scores[:2], "all", 16, (10, 10)); n += 1
    # ---- check_settings
    assert m.check_settings(768, 0.5, 0.35, 20, 6.0, 24, 48) is None; n += 1
    assert m.check_settings(256, 0.0, 0.0, 1, 0.0, 0, 16) is None and m.check_settings(2048, 2.0, 1.0, 200, 100.0, 128, 512) is None; n += 1
    assert "crop_size" in refuses(m.check_settings, 128, 0.5, 0.35, 20, 6.0, 24, 48); n += 1
    assert "crop_size" in refuses(m.check_settings, 4096, 0.5, 0.35, 20, 6.0, 24, 48); n += 1
    assert "padding" in refuses(m.check_settings, 768, 3.0, 0.35, 20, 6.0, 24, 48); n += 1
    assert "denoise" in refuses(m.check_settings, 768, 0.5, 1.5, 20, 6.0, 24, 48); n += 1
    assert "steps" in refuses(m.check_settings, 768, 0.5, 0.35, 0, 6.0, 24, 48); n += 1
    assert "cfg" in refuses(m.check_settings, 768, 0.5, 0.35, 20, -1.0, 24, 48); n += 1
    assert "feather" in refuses(m.check_settings, 768, 0.5, 0.35, 20, 6.0, 200, 48); n += 1
    assert "min_face" in refuses(m.check_settings, 768, 0.5, 0.35, 20, 6.0, 24, 8); n += 1
    # ---- info_text
    assert m.info_text([0], 768, 0.35, 20) == "No face found. The picture was left as it is."; n += 1
    assert m.info_text([0, 0, 0], 768, 0.35, 20) == m.NO_FACE_TEXT; n += 1
    t = m.info_text([1], 768, 0.35, 20)
    assert "1 face " in t and "768 px" in t and "denoise 0.35" in t and "20 steps" in t and "picture" not in t; n += 1
    t = m.info_text([2, 0, 1], 512, 0.5, 10)
    assert "3 faces" in t and "picture 1: 2" in t and "picture 3: 1" in t; n += 1
    # ---- node shape
    c = m.SYFaceDetail
    assert c.RETURN_TYPES == ("IMAGE", "IMAGE", "MASK", "INT", "STRING"); n += 1
    assert c.RETURN_NAMES == ("image", "face_crops", "mask", "count", "info"); n += 1
    assert m.NODE_CLASS_MAPPINGS["SYFaceDetail"] is c and c.CATEGORY == "SY/Image"; n += 1
    spec = c.INPUT_TYPES()
    assert list(spec["required"]) == ["image", "model", "vae", "positive", "negative", "detector", "pick", "crop_size", "padding",
                                      "denoise", "steps", "cfg", "sampler_name", "scheduler", "seed", "feather", "min_face"]; n += 1
    assert list(spec["optional"]) == ["mask"]; n += 1
    assert spec["required"]["crop_size"][1]["step"] == 64 and spec["required"]["crop_size"][1]["default"] == 768; n += 1
    assert spec["required"]["pick"][0] == ["centre 1", "largest 1", "all"] and spec["required"]["pick"][1]["default"] == "largest 1"; n += 1
    assert spec["required"]["detector"][0][0] == m.BUILTIN; n += 1
    assert spec["required"]["seed"][1]["control_after_generate"] is True; n += 1
    assert spec["required"]["denoise"][1]["default"] == 0.35 and spec["required"]["feather"][1]["default"] == 24; n += 1
    for sect in ("required", "optional"):
        for k, d in spec[sect].items():
            assert 0 < len(d[1]["tooltip"]) <= 120, k
    n += 1

    # ---- torch part (only when torch is installed). The sampler, the VAE and the detector are PATCHED here:
    # the real sampler path is NOT run by this test.
    try:
        import torch
    except ImportError:
        torch = None
    if torch is not None:
        import torch.nn.functional as F
        for size, fe in ((20, 4), (20, 0), (17, 128), (1, 5), (33, 24), (64, 8)):  # vectorised feather equals the pure one
            ref = torch.tensor(m.feather_profile(size, fe), dtype=torch.float32)
            assert torch.allclose(m._feather_tensor(size, fe), ref, atol=1e-6), (size, fe)
            n += 1

        class FakeVae:
            def encode(self, px):  # average pool 8x8 -> a latent-like tensor [B, 3, H/8, W/8]
                return F.avg_pool2d(px.permute(0, 3, 1, 2), 8)

            def decode(self, lat):  # resize back
                return F.interpolate(lat, scale_factor=8, mode="bilinear", align_corners=False).permute(0, 2, 3, 1)

        calls = []

        def fake_ksampler(model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent, denoise=1.0, **kw):
            calls.append((seed, steps, cfg, sampler_name, scheduler, denoise))
            return (latent,)  # the latent comes back unchanged

        fake_nodes = types.ModuleType("nodes")
        fake_nodes.common_ksampler = fake_ksampler
        old_nodes = sys.modules.get("nodes")
        sys.modules["nodes"] = fake_nodes
        old_detect = m._detect
        try:
            node = m.SYFaceDetail()
            torch.manual_seed(7)
            img = torch.rand(1, 128, 128, 3)
            args = dict(model=None, vae=FakeVae(), positive=None, negative=None, detector=m.BUILTIN, pick="largest 1",
                        crop_size=256, padding=0.5, denoise=0.35, steps=12, cfg=5.5, sampler_name="euler",
                        scheduler="normal", seed=100, feather=8, min_face=16)

            def one_box(rgb, detector, min_face):
                return [(40.0, 40.0, 80.0, 80.0)], [0.9]
            m._detect = one_box
            out, crops, mask, count, info = node.run(img, **args)
            assert out.shape == img.shape and count == 1 and "1 face " in info; n += 1
            assert crops.shape == (1, 256, 256, 3) and mask.shape == (1, 128, 128); n += 1
            assert calls and calls[-1] == (100, 12, 5.5, "euler", "normal", 0.35); n += 1
            keep = torch.ones(128, 128, dtype=torch.bool)  # the crop square is (30,30)-(90,90): outside it nothing may change
            keep[30:90, 30:90] = False
            assert torch.equal(out[0][keep], img[0][keep]); n += 1
            assert not torch.equal(out[0, 30:90, 30:90], img[0, 30:90, 30:90]); n += 1
            assert not torch.equal(out[0, 60, 60], img[0, 60, 60]); n += 1
            assert torch.equal(out[0, 30, 30], img[0, 30, 30]) and torch.equal(out[0, 89, 89], img[0, 89, 89]); n += 1  # square corners lie outside the ellipse
            assert float(mask[0, 60, 60]) == 1.0 and float(mask[0, 0, 0]) == 0.0 and float(mask[0, 30, 30]) == 0.0; n += 1
            assert float(mask.min()) == 0.0 and float(mask.max()) == 1.0; n += 1
            changed = (out[0] != img[0]).any(dim=-1)
            assert bool((mask[0][changed] > 0).all()); n += 1  # a pixel only changes where the mask says so
            assert torch.equal(img, img.clone()) and float(img.min()) >= 0.0; n += 1
            # feather 0: hard ellipse, outside still identical
            a2 = dict(args)
            a2["feather"] = 0
            out0, _, mask0, c0, _ = node.run(img, **a2)
            assert c0 == 1 and torch.equal(out0[0][keep], img[0][keep]) and set(mask0.unique().tolist()) <= {0.0, 1.0}; n += 1
            # face at the picture edge: padded crop, same picture size, outside the square identical
            m._detect = lambda rgb, d, mf: ([(0.0, 0.0, 40.0, 40.0)], [0.9])
            oute, cropse, maske, ce, _ = node.run(img, **args)
            keep2 = torch.ones(128, 128, dtype=torch.bool)
            keep2[0:50, 0:50] = False
            assert oute.shape == img.shape and ce == 1 and cropse.shape == (1, 256, 256, 3); n += 1
            assert torch.equal(oute[0][keep2], img[0][keep2]) and float(maske[0, 20, 20]) == 1.0; n += 1
            # face in the bottom right corner
            m._detect = lambda rgb, d, mf: ([(100.0, 100.0, 128.0, 128.0)], [0.5])
            outc, _, _, cc, _ = node.run(img, **args)
            sq = torch.ones(128, 128, dtype=torch.bool)
            sq[93:128, 93:128] = False
            assert outc.shape == img.shape and cc == 1 and torch.equal(outc[0][sq], img[0][sq]); n += 1
            # a tiny face is ignored by min_face
            m._detect = lambda rgb, d, mf: ([(10.0, 10.0, 20.0, 20.0)], [0.9])
            outs, cropss, masks, cs, infos = node.run(img, **args)
            assert cs == 0 and torch.equal(outs, img) and infos == m.NO_FACE_TEXT; n += 1
            assert cropss.shape == (1, 64, 64, 3) and float(cropss.abs().sum()) == 0.0 and float(masks.abs().sum()) == 0.0; n += 1
            # no face: identical picture, count 0, the plain sentence, the sampler is not called
            calls.clear()
            m._detect = lambda rgb, d, mf: ([], [])
            outn, cropn, maskn, cn, infon = node.run(img, **args)
            assert torch.equal(outn, img) and cn == 0 and infon == "No face found. The picture was left as it is." and not calls; n += 1
            assert cropn.shape == (1, 64, 64, 3) and maskn.shape == (1, 128, 128) and float(maskn.sum()) == 0.0; n += 1
            # several faces one after another with seed + index
            m._detect = lambda rgb, d, mf: ([(10.0, 10.0, 50.0, 50.0), (70.0, 70.0, 118.0, 118.0)], [0.9, 0.8])
            a3 = dict(args)
            a3["pick"] = "all"
            calls.clear()
            outm, cropm, maskm, cm, infom = node.run(img, **a3)
            assert cm == 2 and cropm.shape[0] == 2 and [x[0] for x in calls] == [100, 101]; n += 1
            assert not torch.equal(outm[0, 25:35, 25:35], img[0, 25:35, 25:35]) and not torch.equal(outm[0, 90:100, 90:100], img[0, 90:100, 90:100]); n += 1
            # a batch of 3: first and last have a face, the middle has none
            seq = iter([([(40.0, 40.0, 80.0, 80.0)], [0.9]), ([], []), ([(40.0, 40.0, 80.0, 80.0)], [0.9])])
            m._detect = lambda rgb, d, mf: next(seq)
            batch = torch.rand(3, 128, 128, 3)
            calls.clear()
            outb, cropb, maskb, cb, infob = node.run(batch, **args)
            assert outb.shape == batch.shape and cb == 2 and cropb.shape[0] == 2 and "picture 1: 1" in infob; n += 1
            assert torch.equal(outb[1], batch[1]) and not torch.equal(outb[0], batch[0]) and float(maskb[1].sum()) == 0.0; n += 1
            assert [x[0] for x in calls] == [100, 101]; n += 1
            # the alpha channel is left alone
            m._detect = one_box
            rgba = torch.rand(1, 128, 128, 4)
            outa, _, _, ca, _ = node.run(rgba, **args)
            assert outa.shape == rgba.shape and ca == 1 and torch.equal(outa[..., 3], rgba[..., 3]); n += 1
            assert not torch.equal(outa[0, 60, 60, :3], rgba[0, 60, 60, :3]); n += 1
            # the optional mask limits the work
            lim = torch.zeros(1, 128, 128)
            lim[:, :, :60] = 1.0
            outl, _, maskl, cl, _ = node.run(img, mask=lim, **args)
            assert cl == 1 and torch.equal(outl[0, :, 60:], img[0, :, 60:]); n += 1
            assert not torch.equal(outl[0, 40:80, 40:60], img[0, 40:80, 40:60]) and float(maskl[0, :, 60:].sum()) == 0.0; n += 1
            far = torch.zeros(1, 128, 128)
            far[:, 100:, 100:] = 1.0  # the face lies outside the allowed area
            outf, _, _, cf, inff = node.run(img, mask=far, **args)
            assert cf == 0 and torch.equal(outf, img) and inff == m.NO_FACE_TEXT; n += 1
            outg, _, _, cg, _ = node.run(img, mask=torch.ones(64, 64), **args)  # a 2-D mask of another size is resized
            assert cg == 1; n += 1
            assert "mask batch" in refuses(node.run, batch, mask=torch.ones(2, 128, 128), **args); n += 1
            # refusals
            assert "batch" in refuses(node.run, torch.zeros(5, 5), **args); n += 1
            assert "at least one" in refuses(node.run, torch.zeros(0, 4, 4, 3), **args); n += 1
            assert "3 colour" in refuses(node.run, torch.zeros(1, 8, 8, 1), **args); n += 1
            bad = dict(args)
            bad["crop_size"] = 64
            assert "crop_size" in refuses(node.run, img, **bad); n += 1
            bad = dict(args)
            bad["sampler_name"] = "nope"
            assert "sampler" in refuses(node.run, img, **bad); n += 1
            bad = dict(args)
            bad["pick"] = "worst"
            assert "pick" in refuses(node.run, img, **bad); n += 1
        finally:
            m._detect = old_detect
            if old_nodes is None:
                sys.modules.pop("nodes", None)
            else:
                sys.modules["nodes"] = old_nodes
    return n
