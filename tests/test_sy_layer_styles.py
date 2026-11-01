import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_layer_styles as m


def refuses(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    return None


def near(a, b, tol=1e-6):
    return abs(a - b) <= tol


def run():
    n = 0
    # ---- gaussian_kernel
    k = m.gaussian_kernel(2.0, 6)
    assert len(k) == 13 and near(sum(k), 1.0) and k == k[::-1]; n += 1
    assert k[6] == max(k) and k[6] > k[5] > k[4] > k[0]; n += 1
    assert m.gaussian_kernel(0, 5) == [1.0] and m.gaussian_kernel(3.0, 0) == [1.0]; n += 1
    assert m.gaussian_kernel(-1, 3) == [1.0]; n += 1
    assert near(sum(m.gaussian_kernel(0.5, 2)), 1.0) and len(m.gaussian_kernel(0.5, 2)) == 5; n += 1
    assert near(m.gaussian_kernel(1.0, 1)[0], m.gaussian_kernel(1.0, 1)[2]); n += 1
    assert refuses(m.gaussian_kernel, 1.0, -1) is not None; n += 1
    # a wider sigma spreads out more
    assert m.gaussian_kernel(4.0, 8)[8] < m.gaussian_kernel(1.0, 8)[8]; n += 1
    assert m.blur_sigma(0) == (0.0, 0) and m.blur_sigma(16) == (8.0, 24) and m.blur_sigma(1) == (0.5, 2); n += 1
    # ---- over_alpha
    assert m.over_alpha((1, 0, 0, 1), (0, 1, 0, 1)) == (1, 0, 0, 1); n += 1
    assert m.over_alpha((1, 0, 0, 0), (0, 1, 0, 1)) == (0, 1, 0, 1); n += 1
    r = m.over_alpha((1, 0, 0, 0.5), (0, 0, 1, 1))
    assert near(r[0], 0.5) and near(r[2], 0.5) and near(r[3], 1.0); n += 1
    r = m.over_alpha((1, 0, 0, 0.5), (0, 0, 1, 0.5))
    assert near(r[3], 0.75) and near(r[0], 2.0 / 3.0) and near(r[2], 1.0 / 3.0); n += 1
    assert m.over_alpha((1, 1, 1, 0), (1, 1, 1, 0)) == (0.0, 0.0, 0.0, 0.0); n += 1
    r = m.over_alpha((0.2, 0.4, 0.6, 1.0), (0.9, 0.9, 0.9, 0.3))
    assert r == (0.2, 0.4, 0.6, 1.0) or all(near(a, b) for a, b in zip(r, (0.2, 0.4, 0.6, 1.0))); n += 1
    r = m.over_alpha((0.5, 0.5, 0.5, 0.0), (0.3, 0.3, 0.3, 0.6))
    assert near(r[3], 0.6) and near(r[0], 0.3); n += 1
    # ---- colour_for
    assert m.colour_for("black", 9, 9, 9) == (0.0, 0.0, 0.0) and m.colour_for("white") == (1.0, 1.0, 1.0); n += 1
    assert m.colour_for("custom", 255, 0, 51) == (1.0, 0.0, 0.2); n += 1
    assert all(0.0 <= v <= 1.0 for name in m.COLOURS for v in m.colour_for(name)); n += 1
    assert list(m.COLOURS) == ["black", "white", "gold", "red", "blue", "green", "grey"] and m.COLOUR_CHOICES[-1] == "custom"; n += 1
    assert m.colour_for("gold")[0] > m.colour_for("gold")[2]; n += 1
    assert "colour must be" in refuses(m.colour_for, "pink"); n += 1
    assert "custom_g" in refuses(m.colour_for, "custom", 0, 300, 0); n += 1
    assert "custom_r" in refuses(m.colour_for, "custom", -1, 0, 0); n += 1
    # ---- disc rows and number checks
    assert m.disc_rows(0) == [(0, 0)]; n += 1
    d = m.disc_rows(3)
    assert d[3] == (0, 3) and d[0] == (-3, 0) and d[6] == (3, 0) and len(d) == 7; n += 1
    assert [e for _, e in d] == [e for _, e in d][::-1]; n += 1
    assert m.check_int("x", 5, 0, 10) == 5 and refuses(m.check_int, "x", 11, 0, 10) and refuses(m.check_int, "x", 1.5, 0, 10); n += 1
    assert "between" in refuses(m.check_float, "opacity", 2, 0, 1) and m.check_float("o", 0.5, 0, 1) == 0.5; n += 1
    # ---- node shape
    D, G, S = m.SYDropShadow, m.SYOuterGlow, m.SYStroke
    for c in (D, G, S):
        assert c.RETURN_TYPES == ("IMAGE", "MASK") and c.RETURN_NAMES == ("image", "effect_mask") and c.CATEGORY == "SY/Image"
        assert "transparent" in c.DESCRIPTION
        spec = c.INPUT_TYPES()
        assert list(spec["optional"]) == ["mask", "custom_r", "custom_g", "custom_b"]
        assert spec["required"]["image"][0] == "IMAGE" and spec["required"]["color"][0] == m.COLOUR_CHOICES
        for sect in ("required", "optional"):
            for key, dd in spec[sect].items():
                assert 0 < len(dd[1]["tooltip"]) <= 120, key
    n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS == {"SYDropShadow": "Drop Shadow SY", "SYOuterGlow": "Outer Glow SY", "SYStroke": "Stroke SY"}; n += 1
    assert set(m.NODE_CLASS_MAPPINGS) == {"SYDropShadow", "SYOuterGlow", "SYStroke"}; n += 1
    sd, sg, ss = D.INPUT_TYPES()["required"], G.INPUT_TYPES()["required"], S.INPUT_TYPES()["required"]
    assert list(sd) == ["image", "offset_x", "offset_y", "blur", "spread", "opacity", "color"]; n += 1
    assert sd["offset_x"][1]["min"] == -512 and sd["offset_x"][1]["max"] == 512 and sd["offset_x"][1]["default"] == 12; n += 1
    assert sd["blur"][1]["max"] == 256 and sd["spread"][1]["min"] == -64 and sd["opacity"][1]["default"] == 0.6 and sd["color"][1]["default"] == "black"; n += 1
    assert list(sg) == ["image", "size", "spread", "opacity", "color"] and sg["size"][1]["default"] == 24 and sg["spread"][1]["default"] == 0.3; n += 1
    assert sg["color"][1]["default"] == "gold"; n += 1
    assert list(ss) == ["image", "width", "position", "opacity", "color"] and ss["width"][1]["default"] == 6 and ss["width"][1]["max"] == 128; n += 1
    assert ss["position"][0] == ["outside", "inside", "centre"] and ss["color"][1]["default"] == "white"; n += 1

    # ---- torch part (only when torch is installed)
    try:
        import torch
    except ImportError:
        torch = None
    if torch is not None:
        def square_rgba(h=60, w=60, s=12, y0=24, x0=24, colour=(1.0, 0.0, 0.0)):
            img = torch.zeros(1, h, w, 4)
            img[0, y0:y0 + s, x0:x0 + s, 0] = colour[0]
            img[0, y0:y0 + s, x0:x0 + s, 1] = colour[1]
            img[0, y0:y0 + s, x0:x0 + s, 2] = colour[2]
            img[0, y0:y0 + s, x0:x0 + s, 3] = 1.0
            return img

        def centre(mask):
            ys, xs = torch.meshgrid(torch.arange(mask.shape[-2], dtype=torch.float32), torch.arange(mask.shape[-1], dtype=torch.float32), indexing="ij")
            tot = float(mask.sum())
            return float((mask[0] * xs).sum()) / tot, float((mask[0] * ys).sum()) / tot

        def bbox(a):
            ys, xs = torch.nonzero(a[0] > 0.001, as_tuple=True)
            return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())

        img = square_rgba()
        # --- helpers on tensors
        m4 = torch.zeros(1, 1, 20, 20)
        m4[..., 10, 10] = 1.0
        d3 = m.dilate(m4, 3)
        assert float(d3.sum()) == sum(2 * e + 1 for _, e in m.disc_rows(3)); n += 1
        assert float(d3[0, 0, 10, 13]) == 1.0 and float(d3[0, 0, 10, 14]) == 0.0 and float(d3[0, 0, 13, 10]) == 1.0 and float(d3[0, 0, 13, 13]) == 0.0; n += 1
        assert torch.equal(m.dilate(m4, 0), m4); n += 1
        full = torch.ones(1, 1, 8, 8)
        assert torch.equal(m.erode(full, 3), full); n += 1       # the picture border does not eat into the shape
        sq = torch.zeros(1, 1, 30, 30)
        sq[..., 10:20, 10:20] = 1.0
        assert float(m.erode(sq, 2).sum()) == 36.0; n += 1
        assert float(m.spread_mask(sq, 0).sum()) == 100.0 and float(m.spread_mask(sq, -2).sum()) == 36.0 and float(m.spread_mask(sq, 2).sum()) > 100.0; n += 1
        sh = m._shift(sq, 5, -3)
        assert float(sh[0, 0, 7, 15]) == 1.0 and float(sh.sum()) == 100.0 and float(m._shift(sq, 100, 0).sum()) == 0.0; n += 1
        sh = m._shift(sq, 15, 0)
        assert float(sh.sum()) == 50.0; n += 1                   # the part pushed past the border is cut
        bl = m.blur_mask(sq, 6)
        assert bl.shape == sq.shape and abs(float(bl.sum()) - 100.0) < 0.5 and 0.0 < float(bl[0, 0, 9, 15]) < 1.0; n += 1
        assert torch.equal(m.blur_mask(sq, 0), sq); n += 1
        assert abs(float(bl[0, 0, 15, 15]) - 1.0) < 0.2 and bool((bl >= 0).all()) and bool((bl <= 1).all()); n += 1
        # blur is symmetric around the shape
        assert abs(float(bl[0, 0, 15, 8]) - float(bl[0, 0, 15, 21])) < 1e-5; n += 1

        # --- Drop Shadow
        ds = D()
        out, em = ds.run(img, 0, 0, 0, 0, 1.0, "black")
        assert out.shape == (1, 60, 60, 4) and em.shape == (1, 60, 60); n += 1
        assert torch.allclose(em[0], img[0, ..., 3]); n += 1                       # no offset, no blur: the shadow is the shape
        out, em = ds.run(img, 9, -5, 0, 0, 1.0, "black")
        c0 = centre(img[..., 3])
        c1 = centre(em)
        assert near(c1[0] - c0[0], 9.0, 1e-4) and near(c1[1] - c0[1], -5.0, 1e-4); n += 1   # shadow centre moved by the offset
        out, em = ds.run(img, -7, 11, 8, 0, 1.0, "black")
        c1 = centre(em)
        assert near(c1[0] - c0[0], -7.0, 0.05) and near(c1[1] - c0[1], 11.0, 0.05); n += 1  # still true with blur
        out, em = ds.run(img, 12, 12, 16, 0, 0.6, "black")
        assert float(em.max()) <= 0.6 + 1e-6 and float(em.max()) > 0.05; n += 1
        # the original stays on top, unchanged
        assert torch.allclose(out[0, 24:36, 24:36, :3], img[0, 24:36, 24:36, :3], atol=1e-5) and float(out[0, 30, 30, 3]) == 1.0; n += 1
        # shadow outside the shape is dark, with alpha
        assert float(out[0, 40, 40, 3]) > 0.1 and float(out[0, 40, 40, :3].max()) < 1e-5; n += 1
        out2, em2 = ds.run(img, 12, 12, 16, 0, 0.6, "white")
        assert float(out2[0, 40, 40, :3].min()) > 0.99; n += 1
        out2, _ = ds.run(img, 12, 12, 0, 0, 1.0, "custom", None, 255, 128, 0)
        assert near(float(out2[0, 40, 40, 0]), 1.0, 1e-4) and near(float(out2[0, 40, 40, 1]), 128 / 255.0, 1e-4); n += 1
        # spread makes it bigger / smaller
        _, e_big = ds.run(img, 0, 0, 0, 4, 1.0, "black")
        _, e_small = ds.run(img, 0, 0, 0, -4, 1.0, "black")
        assert float(e_big.sum()) > float(em2.sum()) * 0 + 144 and float(e_small.sum()) == 16.0; n += 1
        # opacity 0 equals the input (where it can be seen)
        out0, em0 = ds.run(img, 12, 12, 16, 3, 0.0, "black")
        assert float(em0.max()) == 0.0 and torch.allclose(out0, img, atol=1e-6); n += 1
        # RGB picture + mask: outside the mask becomes see-through, the shadow shows
        rgb = torch.rand(1, 60, 60, 3)
        mk = torch.zeros(1, 60, 60)
        mk[:, 20:40, 20:40] = 1.0
        out, em = ds.run(rgb, 10, 10, 0, 0, 1.0, "black", mk)
        assert out.shape == (1, 60, 60, 4) and float(out[0, 5, 5, 3]) == 0.0 and float(out[0, 30, 30, 3]) == 1.0; n += 1
        assert torch.allclose(out[0, 30, 30, :3], rgb[0, 30, 30], atol=1e-5) and float(out[0, 45, 45, 3]) == 1.0 and float(out[0, 45, 45, :3].max()) == 0.0; n += 1
        # batch of two, one mask
        out, em = ds.run(torch.rand(2, 60, 60, 3), 4, 4, 2, 0, 0.5, "grey", mk)
        assert out.shape == (2, 60, 60, 4) and em.shape == (2, 60, 60); n += 1
        # RGBA + mask: alpha times mask
        half_mask = torch.zeros(1, 60, 60)
        half_mask[:, :, :30] = 1.0
        out, _ = ds.run(img, 0, 0, 0, 0, 0.0, "black", half_mask)
        assert float(out[0, 30, 28, 3]) == 1.0 and float(out[0, 30, 32, 3]) == 0.0; n += 1

        # --- Outer Glow
        og = G()
        out, em = og.run(img, 10, 0.3, 1.0, "gold")
        assert out.shape == (1, 60, 60, 4) and em.shape == (1, 60, 60); n += 1
        assert float(em[0, 30, 30]) > 0.9 and float(em[0, 30, 40]) > 0.1 and float(em[0, 30, 40]) < float(em[0, 30, 37]); n += 1   # fades with distance
        assert float(em[0, 30, 4]) < 0.01; n += 1
        assert float(em.sum()) > 144.0; n += 1
        out0, em0 = og.run(img, 24, 0.3, 0.0, "gold")
        assert float(em0.max()) == 0.0 and torch.allclose(out0, img, atol=1e-6); n += 1                  # opacity 0 equals the input
        glow_px = out[0, 30, 40]
        gold = m.COLOURS["gold"]
        assert all(near(float(glow_px[i]), gold[i], 1e-4) for i in range(3)); n += 1
        assert torch.allclose(out[0, 24:36, 24:36, :3], img[0, 24:36, 24:36, :3], atol=1e-5); n += 1       # the picture stays on top
        _, em_a = og.run(img, 16, 0.0, 1.0, "gold")
        _, em_b = og.run(img, 16, 1.0, 1.0, "gold")
        assert float(em_a.sum()) > 143.0 and float(em_b.sum()) > 144 and float(em_b[0, 30, 36 + 16]) == 0.0; n += 1
        assert float(em_b[0, 30, 36 + 16]) < float(em_a[0, 30, 36 + 16]); n += 1                           # spread 1: hard edge, no far reach
        # --- Stroke
        st = S()
        for w in (1, 3, 6):
            out, em = st.run(img, w, "outside", 1.0, "white")
            x0, y0, x1, y1 = bbox(out[..., 3])
            assert (x0, y0, x1, y1) == (24 - w, 24 - w, 35 + w, 35 + w), w                                 # grows by exactly the width
            assert float(out[..., 3].sum()) > 144.0 + 4 * 12 * w - 1
            n += 1
        out, em = st.run(img, 4, "outside", 1.0, "white")
        assert float(em[0, 30, 30]) == 0.0 and float(em[0, 30, 38]) == 1.0 and float(em[0, 30, 41]) == 0.0; n += 1   # only the ring
        assert torch.allclose(out[0, 24:36, 24:36], img[0, 24:36, 24:36], atol=1e-5); n += 1                          # inside untouched
        assert float(out[0, 30, 38, :3].min()) > 0.999 and float(out[0, 30, 38, 3]) == 1.0; n += 1
        out, em = st.run(img, 3, "inside", 1.0, "white")
        assert bbox(out[..., 3]) == (24, 24, 35, 35) and float(em[0, 30, 30]) == 0.0 and float(em[0, 30, 25]) == 1.0; n += 1  # same outline as the shape
        assert float(out[0, 30, 25, :3].min()) > 0.999 and float(out[0, 30, 30, 0]) == 1.0 and float(out[0, 30, 30, 1]) == 0.0; n += 1
        assert float(em.sum()) == 144.0 - 36.0; n += 1
        out, em = st.run(img, 4, "centre", 1.0, "blue")
        assert bbox(out[..., 3]) == (22, 22, 37, 37); n += 1                                                           # half the width outside
        assert float(em[0, 30, 30]) == 0.0 and float(em[0, 30, 23]) == 1.0 and float(em[0, 30, 25]) == 1.0 and float(em[0, 30, 26]) == 0.0; n += 1
        out, em = st.run(img, 5, "centre", 1.0, "blue")
        assert bbox(out[..., 3]) == (21, 21, 38, 38); n += 1                                                           # odd width: 3 out, 2 in
        outz, emz = st.run(img, 5, "outside", 0.0, "white")
        assert float(emz.max()) == 0.0 and torch.allclose(outz, img, atol=1e-6); n += 1
        out, em = st.run(img, 5, "inside", 0.5, "white")
        assert abs(float(em[0, 30, 25]) - 0.5) < 1e-6 and abs(float(out[0, 30, 25, 1]) - 0.5) < 1e-5 and float(out[0, 30, 25, 3]) == 1.0; n += 1
        # stroke by mask on an RGB picture
        out, em = st.run(torch.rand(1, 60, 60, 3), 3, "outside", 1.0, "red", mk)
        assert float(out[0, 18, 30, 3]) == 1.0 and float(out[0, 10, 30, 3]) == 0.0 and float(out[0, 18, 30, 0]) > 0.89; n += 1
        # ---- compositing maths on tensors agrees with the single-pixel function
        base = torch.tensor([[[[0.2, 0.4, 0.6]]]])
        oa = torch.tensor([[[0.5]]])
        la = torch.tensor([[[0.4]]])
        res = m.compose(base, oa, la, (1.0, 0.0, 0.0), over=False)[0, 0, 0]
        ref = m.over_alpha((0.2, 0.4, 0.6, 0.5), (1.0, 0.0, 0.0, 0.4))
        assert all(near(float(res[i]), ref[i], 1e-5) for i in range(4)); n += 1
        res = m.compose(base, oa, la, (1.0, 0.0, 0.0), over=True)[0, 0, 0]
        ref = m.over_alpha((1.0, 0.0, 0.0, 0.4), (0.2, 0.4, 0.6, 0.5))
        assert all(near(float(res[i]), ref[i], 1e-5) for i in range(4)); n += 1
        # ---- refusals
        rgb = torch.rand(1, 20, 20, 3)
        for node, args in ((ds, (0, 0, 0, 0, 1.0, "black")), (og, (8, 0.3, 1.0, "gold")), (st, (3, "outside", 1.0, "white"))):
            assert refuses(node.run, rgb, *args) == m.NEED_SHAPE
            n += 1
        assert "same size" in refuses(ds.run, rgb, 0, 0, 0, 0, 1.0, "black", torch.ones(1, 5, 5)); n += 1
        assert "mask batch" in refuses(ds.run, torch.rand(3, 20, 20, 3), 0, 0, 0, 0, 1.0, "black", torch.ones(2, 20, 20)); n += 1
        assert "mask must be" in refuses(ds.run, rgb, 0, 0, 0, 0, 1.0, "black", torch.ones(1, 20, 20, 1)); n += 1
        assert "expected a picture" in refuses(ds.run, torch.zeros(5, 5), 0, 0, 0, 0, 1.0, "black"); n += 1
        assert "channels" in refuses(ds.run, torch.zeros(1, 5, 5, 1), 0, 0, 0, 0, 1.0, "black", torch.ones(1, 5, 5)); n += 1
        assert "empty" in refuses(ds.run, torch.zeros(0, 5, 5, 4), 0, 0, 0, 0, 1.0, "black"); n += 1
        assert "offset_x" in refuses(ds.run, img, 600, 0, 0, 0, 1.0, "black"); n += 1
        assert "blur" in refuses(ds.run, img, 0, 0, 300, 0, 1.0, "black"); n += 1
        assert "opacity" in refuses(og.run, img, 8, 0.3, 1.5, "gold"); n += 1
        assert "size" in refuses(og.run, img, 0, 0.3, 1.0, "gold"); n += 1
        assert "width" in refuses(st.run, img, 0, "outside", 1.0, "white"); n += 1
        assert "position must" in refuses(st.run, img, 3, "above", 1.0, "white"); n += 1
        assert "colour must" in refuses(st.run, img, 3, "outside", 1.0, "pink"); n += 1
    return n
