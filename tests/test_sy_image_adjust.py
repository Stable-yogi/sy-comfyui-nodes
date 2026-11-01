import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_image_adjust as m


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def near(a, b, eps=1e-4):
    return abs(a - b) < eps


NEUTRAL = (0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.5, 0.0, 1.0, 0.0, 1)


def run():
    n = 0
    # neutral settings are accepted and change nothing
    m.check_settings(*NEUTRAL); n += 1
    px = [0.2, 0.5, 0.8]
    r = m.adjust_pixel(px)
    assert all(near(a, b) for a, b in zip(r, px)); n += 1
    # tone
    r = m.adjust_pixel(px, brightness=0.1)
    assert near(r[0], 0.3) and near(r[1], 0.6) and near(r[2], 0.9); n += 1
    r = m.adjust_pixel([0.25, 0.25, 0.25], gamma=2.0)
    assert near(r[0], 0.5); n += 1
    r = m.adjust_pixel([0.25, 0.5, 0.75], contrast=0.0)
    assert all(near(a, 0.5) for a in r); n += 1
    # colour: saturation 0 is grey with the luma value
    r = m.adjust_pixel([1.0, 0.0, 0.0], saturation=0.0)
    assert near(r[0], r[1]) and near(r[1], r[2]) and near(r[0], 0.2126); n += 1
    # hue 0 is the identity matrix; grey stays grey at any hue
    mat = m.hue_matrix(0)
    assert all(near(a, b) for a, b in zip(mat, (1, 0, 0, 0, 1, 0, 0, 0, 1))); n += 1
    r = m.adjust_pixel([0.4, 0.4, 0.4], hue=120)
    assert all(near(a, 0.4, 1e-3) for a in r); n += 1
    r = m.adjust_pixel([1.0, 0.0, 0.0], hue=120)
    lum_out = 0.2126 * r[0] + 0.7152 * r[1] + 0.0722 * r[2]
    assert r[1] > r[0] and abs(0.2126 - lum_out) < 0.05; n += 1
    # three turns of 120 degrees come back to the start
    r = m.adjust_pixel(m.adjust_pixel(m.adjust_pixel([0.52, 0.47, 0.42], hue=120), hue=120), hue=120)
    assert all(near(a, b, 1e-3) for a, b in zip(r, [0.52, 0.47, 0.42])); n += 1
    # warmth and tint
    g = m.warmth_gains(0.5, 0.0)
    assert g[0] > 1.0 > g[2] and near(g[1], 1.0); n += 1
    g = m.warmth_gains(0.0, 0.5)
    assert g[1] < 1.0 and g[0] > 1.0; n += 1
    r = m.adjust_pixel([0.5, 0.5, 0.5], warmth=1.0)
    assert r[0] > 0.5 > r[2]; n += 1
    # group switches turn a group off
    r = m.adjust_pixel(px, brightness=0.1, use_tone=False)
    assert all(near(a, b) for a, b in zip(r, px)); n += 1
    r = m.adjust_pixel([1.0, 0.0, 0.0], saturation=0.0, use_colour=False)
    assert near(r[0], 1.0); n += 1
    # result always inside 0..1
    r = m.adjust_pixel([0.9, 0.9, 0.9], 1.0, 3.0, 5.0, 3.0, 90, 1.0, 1.0)
    assert all(0.0 <= v <= 1.0 for v in r); n += 1
    # vignette
    assert near(m.vignette_factor(0, 0, 0.8, 1.0), 1.0); n += 1
    assert near(m.vignette_factor(1, 1, 0.8, 1.0), 0.2); n += 1
    assert m.vignette_factor(0.9, 0.9, 0.8, 2.0) > m.vignette_factor(0.9, 0.9, 0.8, 1.0); n += 1
    assert near(m.vignette_factor(1, 1, 0.0, 1.0), 1.0); n += 1
    # refusals: one bad value at a time
    for idx, bad in ((1, -1.0), (2, 0.0), (3, -1.0), (4, 200.0), (5, 2.0), (6, -2.0), (7, -1.0), (8, 0.0), (9, 2.0), (10, 0.0), (11, 2.0), (12, 0)):
        args = list(NEUTRAL)
        args[idx] = bad
        assert raises(m.check_settings, *args), idx
        n += 1
    # active groups and info
    on = (True, True, True, True, True)
    assert m.active_groups(*on, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0) == []; n += 1
    assert m.active_groups(*on, 0.1, 1.0, 1.0, 1.2, 0.0, 0.0, 0.0, 0.5, 0.2, 0.1) == ["tone", "colour", "sharpen", "vignette", "grain"]; n += 1
    assert m.active_groups(False, True, True, True, True, 0.1, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0) == []; n += 1
    assert "switched off" in m.adjust_info([], [], False, 1.0, False); n += 1
    t = m.adjust_info([], ["tone"], True, 1.0, False)
    assert "neutral" in t and "tone switched off" in t; n += 1
    t = m.adjust_info(["tone", "grain"], [], True, 0.5, True)
    assert "tone, grain" in t and "50%" in t and "inside the mask" in t; n += 1
    # torch part: only when torch is installed (the selftest Python has none)
    try:
        import torch
    except ImportError:
        torch = None
    if torch is not None:
        node = m.SYImageAdjust()
        img = torch.rand(2, 24, 32, 3)
        out, info = node.run(img)
        assert torch.equal(out, img) and "neutral" in info; n += 1
        out, info = node.run(img, brightness=0.1, saturation=0.5, sharpen=1.0, vignette=0.4, grain=0.2, grain_seed=3)
        assert out.shape == img.shape and float(out.min()) >= 0.0 and float(out.max()) <= 1.0 and "tone" in info and "grain" in info; n += 1
        out2, _ = node.run(img, grain=0.2, grain_seed=3)
        out3, _ = node.run(img, grain=0.2, grain_seed=3)
        out4, _ = node.run(img, grain=0.2, grain_seed=4)
        assert torch.equal(out2, out3) and not torch.equal(out2, out4); n += 1
        out, info = node.run(img, brightness=0.3, enabled=False)
        assert torch.equal(out, img) and "switched off" in info; n += 1
        out, _ = node.run(img, brightness=0.3, use_tone=False)
        assert torch.equal(out, img); n += 1
        mask = torch.zeros(24, 32)
        mask[:, :16] = 1
        out, info = node.run(img, brightness=0.3, mask=mask)
        assert torch.equal(out[:, :, 20:], img[:, :, 20:]) and not torch.equal(out[:, :, :10], img[:, :, :10]) and "mask" in info; n += 1
        out, _ = node.run(img, brightness=0.3, mix=0.5)
        full, _ = node.run(img, brightness=0.3)
        assert torch.allclose(out, (img + full) / 2, atol=1e-5); n += 1
        rgba = torch.rand(1, 8, 8, 4)
        out, _ = node.run(rgba, brightness=0.2)
        assert torch.equal(out[..., 3], rgba[..., 3]); n += 1
        # torch matches the pure pixel function
        one = torch.tensor([[[[0.3, 0.6, 0.2]]]])
        out, _ = node.run(one, brightness=0.05, contrast=1.2, gamma=1.3, saturation=0.8, hue=40, warmth=0.2, tint=-0.1)
        ref = m.adjust_pixel([0.3, 0.6, 0.2], 0.05, 1.2, 1.3, 0.8, 40, 0.2, -0.1)
        assert all(near(float(a), b, 1e-4) for a, b in zip(out[0, 0, 0], ref)); n += 1
        flat = torch.full((1, 32, 32, 3), 0.5)
        out, _ = node.run(flat, vignette=0.8)
        assert float(out[0, 16, 16, 0]) > float(out[0, 0, 0, 0]) and near(float(out[0, 0, 0, 0]), 0.1, 0.02); n += 1
        edge = torch.zeros(1, 16, 16, 3)
        edge[:, :, 8:] = 1.0
        out, _ = node.run(edge, sharpen=1.5, sharpen_radius=1.5)
        assert float(out[0, 8, 7, 0]) == 0.0 and float(out[0, 8, 8, 0]) == 1.0; n += 1
        assert raises(node.run, torch.rand(1, 4, 4, 1)); n += 1
        assert raises(node.run, img, gamma=0.0); n += 1
    return n


if __name__ == "__main__":
    print("checks:", run())
