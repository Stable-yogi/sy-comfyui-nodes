import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import _sy_lut as L
import sy_apply_lut as m


def refuses(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    return None


def cube_text(size, rows, header=""):
    return "TITLE \"t\"\n# comment\n%sLUT_3D_SIZE %d\n%s" % (header, size, "".join("%r %r %r\n" % r for r in rows))


def close(a, b, tol=1e-6):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def run():
    n = 0
    # ---- identity cube and parse
    ident = L.identity_cube(3)
    assert ident["size"] == 3 and ident["kind"] == "3D" and len(ident["table"]) == 81; n += 1
    assert ident["table"][:6] == [0.0, 0.0, 0.0, 0.5, 0.0, 0.0]; n += 1       # red changes fastest
    assert ident["table"][9:12] == [0.0, 0.5, 0.0]; n += 1                     # then green
    assert ident["table"][27:30] == [0.0, 0.0, 0.5]; n += 1                    # then blue
    rows = [(ident["table"][i], ident["table"][i + 1], ident["table"][i + 2]) for i in range(0, 81, 3)]
    p = L.parse_cube(cube_text(3, rows))
    assert p["size"] == 3 and p["kind"] == "3D" and p["table"] == ident["table"]; n += 1
    assert p["domain_min"] == (0.0, 0.0, 0.0) and p["domain_max"] == (1.0, 1.0, 1.0); n += 1
    p = L.parse_cube(cube_text(3, rows, "DOMAIN_MIN 0 0 0\nDOMAIN_MAX 2 2 2\n"))
    assert p["domain_max"] == (2.0, 2.0, 2.0); n += 1
    assert close(L.sample_cube(p, (1.0, 1.0, 1.0)), (0.5, 0.5, 0.5)); n += 1   # domain honoured
    p = L.parse_cube("LUT_3D_SIZE 2\r\n" + "".join("%d %d %d\r\n" % (r, g, b) for b in (0, 1) for g in (0, 1) for r in (0, 1)))
    assert p["size"] == 2 and p["table"][3:6] == [1.0, 0.0, 0.0]; n += 1
    # ---- 1D example
    one = L.parse_cube("LUT_1D_SIZE 2\n0 0 0\n1 0.5 0\n")
    assert one["kind"] == "1D" and one["size"] == 2 and len(one["table"]) == 6; n += 1
    assert close(L.sample_cube(one, (0.5, 0.5, 0.5)), (0.5, 0.25, 0.0)); n += 1
    assert close(L.sample_cube(one, (1.0, 1.0, 1.0)), (1.0, 0.5, 0.0)); n += 1
    one4 = L.parse_cube("LUT_1D_SIZE 4\n0 0 0\n0.1 0.1 0.1\n0.5 0.5 0.5\n1 1 1\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n")
    assert close(L.sample_cube(one4, (1.0 / 3, 2.0 / 3, 1.0)), (0.1, 0.5, 1.0)); n += 1
    # ---- refusals
    assert "no size" in refuses(L.parse_cube, "0 0 0\n"); n += 1
    assert "no size" in refuses(L.parse_cube, ""); n += 1
    assert "between 2 and 65" in refuses(L.parse_cube, "LUT_3D_SIZE 1\n0 0 0\n"); n += 1
    assert "between 2 and 65" in refuses(L.parse_cube, "LUT_3D_SIZE 66\n"); n += 1
    assert "whole number" in refuses(L.parse_cube, "LUT_3D_SIZE two\n"); n += 1
    assert "needs 8 rows" in refuses(L.parse_cube, "LUT_3D_SIZE 2\n0 0 0\n1 1 1\n"); n += 1
    assert "needs 8 rows" in refuses(L.parse_cube, "LUT_3D_SIZE 2\n" + "0 0 0\n" * 9); n += 1
    assert "not a number" in refuses(L.parse_cube, "LUT_3D_SIZE 2\n" + "0 0 x\n" * 8) and "line 2" in refuses(L.parse_cube, "LUT_3D_SIZE 2\n" + "0 0 x\n" * 8); n += 1
    assert "exactly three" in refuses(L.parse_cube, "LUT_3D_SIZE 2\n0 0\n"); n += 1
    assert "ordinary numbers" in refuses(L.parse_cube, "LUT_3D_SIZE 2\n" + "0 0 nan\n" * 8); n += 1
    assert "both" in refuses(L.parse_cube, "LUT_3D_SIZE 2\nLUT_1D_SIZE 2\n"); n += 1
    assert "DOMAIN_MAX" in refuses(L.parse_cube, "DOMAIN_MIN 1 1 1\nDOMAIN_MAX 0 0 0\nLUT_1D_SIZE 2\n0 0 0\n1 1 1\n"); n += 1
    assert "three numbers" in refuses(L.parse_cube, "DOMAIN_MIN 0 0\nLUT_1D_SIZE 2\n"); n += 1
    assert "text" in refuses(L.parse_cube, 5); n += 1
    assert "bigger than 20 MB" in refuses(L.parse_cube, "x" * (L.MAX_FILE_BYTES + 1)); n += 1
    # ---- built-in looks
    assert len(L.BUILTIN_NAMES) == 7 and L.BUILTIN_NAMES[0] == "none"; n += 1
    for name in L.BUILTIN_NAMES:
        c = L.builtin_cube(name)
        assert c["size"] == 17 and len(c["table"]) == 17 ** 3 * 3 and all(0.0 <= v <= 1.0 for v in c["table"]), name
        again = L.parse_cube("LUT_3D_SIZE 17\n" + "".join("%r %r %r\n" % tuple(c["table"][i:i + 3]) for i in range(0, len(c["table"]), 3)))
        assert again["table"] == c["table"], name
        n += 1
    assert L.builtin_cube("none", 5)["table"] == L.identity_cube(5)["table"]; n += 1
    assert "Unknown built-in" in refuses(L.builtin_cube, "sepia"); n += 1
    assert "between 2 and 65" in refuses(L.builtin_cube, "warm", 1); n += 1
    bw = L.builtin_cube("black and white")
    for px in ((0.9, 0.2, 0.1), (0.1, 0.8, 0.3), (0.0, 0.0, 1.0)):
        o = L.sample_cube(bw, px)
        assert abs(o[0] - o[1]) < 1e-6 and abs(o[1] - o[2]) < 1e-6
    n += 1
    w = L.sample_cube(L.builtin_cube("warm"), (0.5, 0.5, 0.5))
    assert w[0] > w[2]; n += 1
    c = L.sample_cube(L.builtin_cube("cool"), (0.5, 0.5, 0.5))
    assert c[2] > c[0]; n += 1
    hc = L.builtin_cube("high contrast")
    assert L.sample_cube(hc, (0.25, 0.25, 0.25))[0] < 0.25 and L.sample_cube(hc, (0.75, 0.75, 0.75))[0] > 0.75; n += 1
    ff = L.sample_cube(L.builtin_cube("faded film"), (0.0, 0.0, 0.0))
    assert ff[0] > 0.05; n += 1
    assert close(L.sample_cube(L.identity_cube(9), (0.31, 0.62, 0.93)), (0.31, 0.62, 0.93), 1e-9); n += 1
    # ---- name helpers
    ch = m.lut_choices(["b.cube", "a.cube", "readme.txt", "a.cube", "sub/c.CUBE"])
    assert ch[:7] == list(L.BUILTIN_NAMES) and ch[7:] == ["a.cube", "b.cube", "sub/c.CUBE"]; n += 1
    assert m.lut_choices(None) == list(L.BUILTIN_NAMES); n += 1
    assert refuses(m.check_lut_name, "../x.cube") and refuses(m.check_lut_name, "a/../../x.cube"); n += 1
    assert refuses(m.check_lut_name, "/etc/x.cube") and refuses(m.check_lut_name, "C:/x.cube") and refuses(m.check_lut_name, "C:\\x.cube"); n += 1
    assert refuses(m.check_lut_name, "x.png") and refuses(m.check_lut_name, ""); n += 1
    assert m.check_lut_name("sub\\x.cube") == "sub/x.cube"; n += 1
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "sub"))
        with open(os.path.join(d, "sub", "x.cube"), "w") as f:
            f.write("LUT_1D_SIZE 2\n0 0 0\n1 1 1\n")
        found = m.resolve_lut_path("sub/x.cube", ["/nonexistent-folder", d])
        assert os.path.isfile(found); n += 1
        assert "not found" in refuses(m.resolve_lut_path, "nope.cube", [d]); n += 1
        assert refuses(m.resolve_lut_path, "../sub/x.cube", [d]) is not None; n += 1
    # ---- pick_cube
    assert m.pick_cube("none", "") is None and m.pick_cube("none", "   ") is None; n += 1
    assert m.pick_cube("warm", "")["size"] == 17; n += 1
    assert m.pick_cube("warm", "LUT_1D_SIZE 2\n0 0 0\n1 1 1\n")["kind"] == "1D"; n += 1   # text wins
    assert "table row" in refuses(m.pick_cube, "none", "garbage 1 2 3 4"); n += 1
    # ---- node shape
    c = m.SYApplyLUT
    assert c.RETURN_TYPES == ("IMAGE",) and c.RETURN_NAMES == ("image",); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYApplyLUT"] == "Apply LUT SY" and m.NODE_CLASS_MAPPINGS["SYApplyLUT"] is c; n += 1
    spec = c.INPUT_TYPES()
    assert list(spec["required"]) == ["image", "lut", "strength"] and list(spec["optional"]) == ["lut_text"]; n += 1
    assert spec["required"]["lut"][0][:7] == list(L.BUILTIN_NAMES) and spec["required"]["lut"][1]["default"] == "none"; n += 1
    assert spec["optional"]["lut_text"][1]["multiline"] is True; n += 1
    for sect in ("required", "optional"):
        for k, dd in spec[sect].items():
            assert 0 < len(dd[1]["tooltip"]) <= 120, k
    n += 1
    assert c.CATEGORY == "SY/Image" and "alpha" in c.DESCRIPTION; n += 1

    # ---- torch part (only when torch is installed)
    try:
        import torch
    except ImportError:
        torch = None
    if torch is not None:
        node = c()
        img = torch.rand(2, 9, 11, 3)
        # identity table through the real sampler
        for size in (2, 5, 17):
            out = m.apply_cube_tensor(img, L.identity_cube(size), 1.0)
            assert float((out - img).abs().max()) < 1e-4, size
            n += 1
        out = node.run(img, "none", 1.0, "LUT_3D_SIZE 2\n" + "".join("%d %d %d\n" % (r, g, b) for b in (0, 1) for g in (0, 1) for r in (0, 1)))[0]
        assert float((out - img).abs().max()) < 1e-4; n += 1
        # torch agrees with the plain-Python sampler on a real look
        look = L.builtin_cube("teal and orange")
        got = m.apply_cube_tensor(img, look, 1.0)
        for (bi, yi, xi) in ((0, 0, 0), (1, 4, 5), (0, 8, 10)):
            ref = L.sample_cube(look, [float(v) for v in img[bi, yi, xi]])
            assert close([float(v) for v in got[bi, yi, xi]], ref, 1e-4)
        n += 1
        # black and white gives equal channels
        out = node.run(img, "black and white", 1.0)[0]
        assert float((out[..., 0] - out[..., 1]).abs().max()) < 1e-4 and float((out[..., 1] - out[..., 2]).abs().max()) < 1e-4; n += 1
        # strength 0 = input, strength 0.5 halfway
        out = node.run(img, "warm", 0.0)[0]
        assert torch.equal(out, img); n += 1
        full = node.run(img, "warm", 1.0)[0]
        half = node.run(img, "warm", 0.5)[0]
        assert float((half - (img + full) / 2).abs().max()) < 1e-4; n += 1
        assert float((full - img).abs().max()) > 0.01; n += 1
        # none returns the same picture
        assert torch.equal(node.run(img, "none", 1.0)[0], img); n += 1
        # alpha untouched, shape kept
        rgba = torch.rand(1, 6, 7, 4)
        out = node.run(rgba, "cool", 1.0)[0]
        assert out.shape == rgba.shape and torch.equal(out[..., 3], rgba[..., 3]); n += 1
        assert float((out[..., :3] - rgba[..., :3]).abs().max()) > 0.001; n += 1
        # output stays in range and is finite
        for name in L.BUILTIN_NAMES:
            o = node.run(img, name, 1.0)[0]
            assert float(o.min()) >= 0.0 and float(o.max()) <= 1.0 and bool(torch.isfinite(o).all()), name
        n += 1
        # 1D table: invert
        inv = "LUT_1D_SIZE 2\n1 1 1\n0 0 0\n"
        o = node.run(img, "none", 1.0, inv)[0]
        assert float((o - (1.0 - img)).abs().max()) < 1e-4; n += 1
        # domain honoured
        dom = "DOMAIN_MIN 0 0 0\nDOMAIN_MAX 2 2 2\nLUT_1D_SIZE 2\n0 0 0\n1 1 1\n"
        o = node.run(torch.full((1, 2, 2, 3), 1.0), "none", 1.0, dom)[0]
        assert abs(float(o[0, 0, 0, 0]) - 0.5) < 1e-4; n += 1
        # values outside 0..1 are clamped
        o = node.run(torch.full((1, 2, 2, 3), 1.7), "none", 1.0, inv)[0]
        assert float(o.max()) <= 1.0 and float(o.min()) >= 0.0; n += 1
        # refusals through the node
        assert "strength" in refuses(node.run, img, "warm", 1.5); n += 1
        assert "no size" in refuses(node.run, img, "none", 1.0, "1 2 3"); n += 1
        assert "expected a picture" in refuses(node.run, torch.zeros(4, 4), "warm", 1.0); n += 1
        assert "channels" in refuses(node.run, torch.zeros(1, 4, 4, 1), "warm", 1.0); n += 1
        assert refuses(node.run, img, "../evil.cube", 1.0) is not None; n += 1
    return n
