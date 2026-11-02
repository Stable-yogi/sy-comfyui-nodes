import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_gradient_map as m


def raises(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def near(a, b, tol=1e-6):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def run():
    n = 0

    def ok(cond, msg="check failed"):
        nonlocal n
        n += 1
        if not cond:
            raise SystemExit("gradient map: " + msg)

    ok(m.parse_hex("fff") == (1.0, 1.0, 1.0), "short hex")
    ok(m.parse_hex("#" + "ff0000") == (1.0, 0.0, 0.0), "long hex")
    ok(near(m.parse_hex("#" + "0f0"), (0.0, 1.0, 0.0)), "short hex with hash")
    ok(raises(m.parse_hex, "zzz"), "bad digits")
    ok(raises(m.parse_hex, "12345"), "bad length")
    ok(raises(m.parse_hex, ""), "empty")
    ok(abs(m.luma(1, 1, 1) - 1.0) < 1e-9 and m.luma(0, 0, 0) == 0.0, "luma ends")
    ok(m.luma(0, 1, 0) > m.luma(1, 0, 0) > m.luma(0, 0, 1), "rec709 weights order")
    two = [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)]
    ok(m.gradient_color(0.0, two) == (0.0, 0.0, 0.0) and m.gradient_color(1.0, two) == (1.0, 1.0, 1.0), "two stop ends")
    ok(near(m.gradient_color(0.25, two), (0.25, 0.25, 0.25)), "two stop mid")
    three = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]
    ok(m.gradient_color(0.5, three) == (0.0, 1.0, 0.0), "three stop middle")
    ok(near(m.gradient_color(0.25, three), (0.5, 0.5, 0.0)), "three stop first half")
    ok(m.gradient_color(1.0, three) == (0.0, 0.0, 1.0), "three stop end")
    ok(m.gradient_color(5.0, two) == (1.0, 1.0, 1.0) and m.gradient_color(-1.0, two) == (0.0, 0.0, 0.0), "clamps")
    ok(raises(m.gradient_color, 0.5, [(0, 0, 0)]), "one stop")
    ok(len(m.build_stops("000", "fff")) == 2 and len(m.build_stops("000", "fff", "  ")) == 2, "empty colour 3 is off")
    ok(len(m.build_stops("000", "fff", "f00")) == 3 and m.build_stops("000", "fff", "f00")[1] == (1.0, 0.0, 0.0), "colour 3 is the middle")
    ok(raises(m.build_stops, "000", "nope"), "bad colour 2")
    ok(raises(m.build_stops, "000", "fff", "oops"), "bad colour 3")
    ok(raises(m.check_strength, 1.5), "bad strength")
    red = [(1.0, 0.0, 0.0), (0.0, 0.0, 1.0)]
    ok(near(m.map_pixel((0.0, 0.0, 0.0), red), (1.0, 0.0, 0.0)), "black gets colour 1")
    ok(near(m.map_pixel((1.0, 1.0, 1.0), red), (0.0, 0.0, 1.0)), "white gets colour 2")
    ok(near(m.map_pixel((1.0, 1.0, 1.0), red, invert=True), (1.0, 0.0, 0.0)), "invert swaps")
    ok(near(m.map_pixel((0.3, 0.3, 0.3), red, strength=0.0), (0.3, 0.3, 0.3)), "strength 0 keeps original")
    ok(near(m.map_pixel((0.0, 0.0, 0.0), red, mask=0.0), (0.0, 0.0, 0.0)), "mask 0 keeps original")
    ok(m.NODE_DISPLAY_NAME_MAPPINGS["SYGradientMap"] == "Gradient Map SY", "display name")

    try:
        import torch
    except ImportError:
        torch = None
    if torch is not None:
        node = m.SYGradientMap()
        img = torch.zeros(2, 4, 4, 3)
        img[1] = 1.0
        (out,) = node.run(img, "f00", "00f", 1.0, False)
        ok(out.shape == img.shape, "shape")
        ok(torch.allclose(out[0, 0, 0], torch.tensor([1.0, 0.0, 0.0]), atol=1e-4), "black becomes colour 1")
        ok(torch.allclose(out[1, 0, 0], torch.tensor([0.0, 0.0, 1.0]), atol=1e-4), "white becomes colour 2")
        (inv,) = node.run(img, "f00", "00f", 1.0, True)
        ok(torch.allclose(inv[0, 0, 0], torch.tensor([0.0, 0.0, 1.0]), atol=1e-4), "invert")
        grey = torch.full((1, 2, 2, 3), 0.5)
        (mid,) = node.run(grey, "000", "fff", 1.0, False, "f00")
        ok(torch.allclose(mid[0, 0, 0], torch.tensor([1.0, 0.0, 0.0]), atol=2e-3), "middle colour")
        (half,) = node.run(grey, "000", "fff", 0.0, False)
        ok(torch.allclose(half, grey), "strength 0")
        mask = torch.zeros(1, 4, 4)
        mask[:, :, 2:] = 1.0
        (mk,) = node.run(img[:1], "f00", "00f", 1.0, False, "", mask)
        ok(float(mk[0, 0, 0, 0]) == 0.0 and abs(float(mk[0, 0, 3, 0]) - 1.0) < 1e-4, "mask limits the effect")
        (small,) = node.run(img[:1], "f00", "00f", 1.0, False, "", torch.ones(1, 2, 2))
        ok(small.shape == img[:1].shape, "mask of other size is stretched")
        rgba = torch.rand(1, 3, 3, 4)
        (a4,) = node.run(rgba, "000", "fff", 1.0, False)
        ok(torch.equal(a4[..., 3], rgba[..., 3]), "alpha kept")
        try:
            node.run(img, "nope", "fff", 1.0, False)
            ok(False, "should raise")
        except ValueError:
            ok(True)
    return n
