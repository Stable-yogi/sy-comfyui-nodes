import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_tone_curve as m


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def near(a, b, eps=1e-4):
    return abs(a - b) < eps


def run():
    n = 0
    # parsing
    assert m.parse_curve_points("") == [] and m.parse_curve_points("   \n ") == [] and m.parse_curve_points(None) == []; n += 1
    p = m.parse_curve_points("0,0 0.25,0.2 0.75,0.85 1,1")
    assert p == [(0.0, 0.0), (0.25, 0.2), (0.75, 0.85), (1.0, 1.0)]; n += 1
    p = m.parse_curve_points("0.25,0.2;0.75,0.85\n")
    assert p[0] == (0.0, 0.0) and p[-1] == (1.0, 1.0) and len(p) == 4; n += 1
    for bad in ("abc", "0.5", "0.5,0.5,0.5", "0.5,x", "1.5,0.2", "0.2,-0.1", "0.6,0.6 0.5,0.5", "0.5,0.5 0.5,0.6", "nan,0.5", "0.5,",
                " ".join("%.4f,0.5" % (i / 100.0) for i in range(70))):
        assert raises(m.parse_curve_points, bad), bad
        n += 1
    # smooth monotone curve
    lut = m.curve_lut(m.parse_curve_points("0,0 0.25,0.1 0.75,0.9 1,1"))
    assert len(lut) == 256 and near(lut[0], 0.0) and near(lut[255], 1.0) and near(lut[64], 0.1, 0.01); n += 1
    assert all(lut[i + 1] >= lut[i] - 1e-9 for i in range(255)); n += 1
    assert all(0.0 <= v <= 1.0 for v in lut); n += 1
    # a sharp bend does not overshoot
    lut = m.curve_lut([(0.0, 0.0), (0.5, 0.05), (0.52, 0.95), (1.0, 1.0)])
    assert all(lut[i + 1] >= lut[i] - 1e-9 for i in range(255)) and max(lut) <= 1.0; n += 1
    # straight line when no points; two-point decreasing curve is the invert line
    lut = m.curve_lut([])
    assert near(lut[128], 128 / 255.0); n += 1
    lut = m.curve_lut(m.PRESETS["invert"])
    assert near(lut[0], 1.0) and near(lut[255], 0.0) and near(lut[51], 0.8, 1e-3); n += 1
    # presets
    assert m.preset_points("none") == []; n += 1
    for name in m.PRESET_NAMES[1:]:
        pts = m.preset_points(name)
        assert len(pts) >= 2 and all(0.0 <= a <= 1.0 and 0.0 <= b <= 1.0 for a, b in pts), name
        assert all(pts[i + 1][0] > pts[i][0] for i in range(len(pts) - 1)); n += 2
    assert raises(m.preset_points, "sepia"); n += 1
    assert m.curve_lut(m.PRESETS["strong contrast"])[64] < m.curve_lut(m.PRESETS["soft contrast"])[64] < 0.25; n += 1
    assert m.curve_lut(m.PRESETS["lift shadows"])[64] > 0.25; n += 1
    assert near(m.curve_lut(m.PRESETS["fade blacks"])[0], 0.10); n += 1
    # typed points win over the preset
    pts, label = m.choose_curve("0,0 0.5,0.7 1,1", "invert")
    assert len(pts) == 3 and "your own" in label; n += 1
    pts, label = m.choose_curve("", "invert")
    assert pts == list(m.PRESETS["invert"]) and "invert" in label; n += 1
    assert m.choose_curve("", "none") == ([], ""); n += 1
    # auto levels from a histogram
    hist = [0] * 256
    for i in range(77, 154):
        hist[i] = 10
    lo, hi = m.auto_level_points(hist, 0.0)
    assert near(lo, 77 / 255.0) and near(hi, 153 / 255.0); n += 1
    lo2, hi2 = m.auto_level_points(hist, 10.0)
    assert lo2 > lo and hi2 < hi; n += 1
    hist[0], hist[255] = 3, 3   # a few stray pixels are ignored by the clip
    lo, hi = m.auto_level_points(hist, 1.0)
    assert lo > 70 / 255.0 and hi < 160 / 255.0; n += 1
    assert m.auto_level_points([0] * 256, 0.5) == (0.0, 1.0); n += 1
    flat = [0] * 256
    flat[100] = 500
    assert m.auto_level_points(flat, 0.5) == (0.0, 1.0); n += 1
    # levels
    assert near(m.levels_value(0.5), 0.5); n += 1
    assert near(m.levels_value(0.2, black=0.2), 0.0) and near(m.levels_value(0.8, white=0.8), 1.0); n += 1
    assert m.levels_value(0.25, midtone=2.0) > 0.25 > m.levels_value(0.25, midtone=0.5); n += 1
    assert near(m.levels_value(0.3, lo=0.2, hi=0.4), 0.5); n += 1
    lut = m.build_lut()
    assert all(near(lut[i], i / 255.0, 1e-9) for i in range(256)); n += 1
    lut = m.build_lut(0.2, 0.8, 0.0, 1.0, 1.0, m.PRESETS["invert"])
    assert near(lut[0], 1.0) and near(lut[255], 0.0); n += 1
    # settings refusals
    ok = ("off", 0.5, 0.0, 1.0, 1.0, "none", 256)
    m.check_settings(*ok); n += 1
    for idx, bad in ((0, "maybe"), (1, -1.0), (1, 11.0), (2, -0.1), (2, 0.96), (3, 0.0), (3, 1.5), (4, 0.0), (4, 6.0), (5, "sepia"), (6, 10), (6, 600)):
        args = list(ok)
        args[idx] = bad
        assert raises(m.check_settings, *args), (idx, bad)
        n += 1
    assert raises(m.check_settings, "off", 0.5, 0.9, 0.5, 1.0, "none", 256); n += 1
    assert raises(m.check_settings, "off", 0.5, 0.9, 0.905, 1.0, "none", 256); n += 1
    # neutral and info
    assert m.is_neutral("off", 0.0, 1.0, 1.0, []); n += 1
    assert not m.is_neutral("per picture", 0.0, 1.0, 1.0, []); n += 1
    assert not m.is_neutral("off", 0.0, 1.0, 1.0, m.PRESETS["invert"]); n += 1
    assert "switched off" in m.tone_info(False, "", "", "", 1.0, False, False); n += 1
    assert "neutral" in m.tone_info(True, "", "", "", 1.0, False, False); n += 1
    txt = m.describe_levels([(0.06, 0.06, 0.06)], [(0.93, 0.93, 0.93)], 0.5, False)
    assert txt == "black 0.06, white 0.93, clipped 0.5%", txt; n += 1
    txt = m.describe_levels([(0.1, 0.2, 0.3), (0.12, 0.2, 0.3)], [(0.9, 0.9, 0.9)] * 2, 1.0, True)
    assert "R 0.10-0.12" in txt and "G 0.20" in txt; n += 1
    t = m.tone_info(True, txt, "preset invert", "midtone 1.2", 0.5, True, True)
    assert "auto levels found" in t and "preset invert" in t and "midtone 1.2" in t and "50%" in t and "inside the mask" in t; n += 1
    assert "no curve" in m.tone_info(True, "", "", "midtone 2", 1.0, False, True); n += 1
    # torch part: only when torch is installed (the selftest Python has none)
    try:
        import torch
    except ImportError:
        return n
    node = m.SYToneCurve()
    gen = torch.Generator().manual_seed(7)
    img = torch.rand(2, 16, 20, 3, generator=gen)
    # neutral settings give the identical picture
    out, hist, info = node.run(img)
    assert out is img and "neutral" in info; n += 1
    assert hist.shape == (1, 128, 256, 3) and 0.0 <= float(hist.min()) and float(hist.max()) <= 1.0; n += 1
    out, hist, info = node.run(img, enabled=False)
    assert torch.equal(out, img) and "switched off" in info; n += 1
    out, _, _ = node.run(img, curve_preset="invert", enabled=False)
    assert torch.equal(out, img); n += 1
    # invert preset
    out, hist, info = node.run(img, curve_preset="invert")
    assert float((out - (1.0 - img)).abs().max()) < 2e-3 and "invert" in info; n += 1
    # typed points replace the preset
    out, _, info = node.run(img, curve_points="0,0 1,1", curve_preset="invert")
    assert float((out - img).abs().max()) < 2e-3 and "your own" in info; n += 1
    # midtone brightens, black/white point stretch
    out, _, _ = node.run(img, midtone=2.0)
    assert float(out.mean()) > float(img.mean()); n += 1
    flat = torch.full((1, 8, 8, 3), 0.5)
    out, _, _ = node.run(flat, black_point=0.5, white_point=1.0)
    assert float(out.max()) < 0.01; n += 1
    # auto levels stretch a low-contrast picture
    low = 0.3 + 0.3 * torch.rand(1, 32, 32, 3, generator=gen)
    out, _, info = node.run(low, auto_levels="per picture", clip_percent=0.5)
    assert float(out.min()) < 0.03 and float(out.max()) > 0.97 and "auto levels found black" in info and "clipped 0.5%" in info; n += 1
    out, _, info = node.run(low, auto_levels="whole batch", clip_percent=0.0)
    assert float(out.min()) < 0.02 and float(out.max()) > 0.98; n += 1
    # per picture vs whole batch: a dark and a bright picture
    pair = torch.cat([0.1 + 0.2 * torch.rand(1, 16, 16, 3, generator=gen), 0.6 + 0.3 * torch.rand(1, 16, 16, 3, generator=gen)])
    out_p, _, _ = node.run(pair, auto_levels="per picture", clip_percent=0.0)
    out_b, _, _ = node.run(pair, auto_levels="whole batch", clip_percent=0.0)
    assert float(out_p[0].max()) > 0.97 and float(out_b[0].max()) < 0.6; n += 1
    # per_channel removes a colour cast
    g = torch.linspace(0.0, 1.0, 32).view(1, 1, 32, 1).expand(1, 32, 32, 1)
    cast = torch.cat([0.5 + 0.4 * g, 0.1 + 0.4 * g, 0.0 + 0.4 * g], dim=-1)
    before = [float(cast[..., k].mean()) for k in range(3)]
    out, _, info = node.run(cast, auto_levels="per picture", clip_percent=0.0, per_channel=True)
    after = [float(out[..., k].mean()) for k in range(3)]
    assert max(before) - min(before) > 0.3 and max(after) - min(after) < 0.03 and "R " in info; n += 1
    out, _, _ = node.run(cast, auto_levels="per picture", clip_percent=0.0, per_channel=False)
    after = [float(out[..., k].mean()) for k in range(3)]
    assert max(after) - min(after) > 0.2; n += 1
    # mask: outside untouched, inside changed; mix 0 is the original
    mask = torch.zeros(1, 16, 20)
    mask[:, :, 10:] = 1.0
    out, _, info = node.run(img, curve_preset="invert", mask=mask)
    assert torch.equal(out[:, :, :10], img[:, :, :10]) and float((out[:, :, 10:] - img[:, :, 10:]).abs().max()) > 0.0 and "inside the mask" in info; n += 1
    out, _, _ = node.run(img, curve_preset="invert", mix=0.0)
    assert torch.allclose(out, img); n += 1
    out, _, info = node.run(img, curve_preset="invert", mix=0.5)
    assert float((out - 0.5).abs().max()) < 2e-3 and "50%" in info; n += 1
    # alpha is kept
    rgba = torch.rand(1, 8, 8, 4, generator=gen)
    out, _, _ = node.run(rgba, curve_preset="invert")
    assert out.shape[3] == 4 and torch.equal(out[..., 3], rgba[..., 3]); n += 1
    # histogram size and shape
    _, hist, _ = node.run(img, curve_preset="soft contrast", histogram_size=128)
    assert hist.shape == (1, 64, 128, 3); n += 1
    _, hist, _ = node.run(img, curve_preset="soft contrast", histogram_size=512)
    assert hist.shape == (1, 256, 512, 3); n += 1
    # histogram of a picture with a single grey level: grey bar, one colour line column
    grey = torch.full((1, 8, 8, 3), 0.5)
    _, hist, _ = node.run(grey, midtone=1.5)
    assert float(hist.std()) > 0.0; n += 1
    # refusals
    assert raises(node.run, torch.rand(1, 4, 4, 1)); n += 1
    assert raises(node.run, torch.rand(4, 4, 3)); n += 1
    assert raises(node.run, img, curve_points="0.5,2"); n += 1
    assert raises(node.run, img, curve_points="0.6,0.6 0.5,0.5"); n += 1
    assert raises(node.run, img, black_point=0.9, white_point=0.5); n += 1
    assert raises(node.run, img, mix=1.5); n += 1
    assert raises(node.run, img, curve_preset="invert", mask=torch.zeros(3, 16, 20)); n += 1
    assert raises(node.run, img, midtone=0.0); n += 1
    return n


if __name__ == "__main__":
    print("checks:", run())
