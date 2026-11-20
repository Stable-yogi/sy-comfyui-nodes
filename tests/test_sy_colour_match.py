import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_colour_match as m


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
    assert m.mean_std([0.0, 1.0]) == (0.5, 0.5); n += 1
    assert near(m.mean_std([0.3] * 4)[1], 0.0); n += 1
    out = m.match_values([0.2, 0.4, 0.6], 0.5, 0.1, 1.0)
    mean, std = m.mean_std(out)
    assert near(mean, 0.5) and near(std, 0.1); n += 1
    src = [0.2, 0.4, 0.6]
    assert m.match_values(src, 0.9, 0.3, 0.0) == src; n += 1
    half = m.match_values([0.2, 0.4, 0.6], 0.5, 0.1, 0.5)
    full = m.match_values([0.2, 0.4, 0.6], 0.5, 0.1, 1.0)
    assert near(half[0], (0.2 + full[0]) / 2.0); n += 1
    flat = m.match_values([0.5, 0.5], 0.8, 0.2, 1.0)
    assert near(flat[0], 0.8) and near(flat[1], 0.8); n += 1
    assert all(0.0 <= v <= 1.0 for v in m.match_values([0.0, 1.0], 0.5, 5.0, 1.0)); n += 1
    assert raises(m.match_values, [0.1], 0.5, 0.1, 2.0); n += 1
    assert raises(m.mean_std, []); n += 1
    spec = m.SYColourMatch.INPUT_TYPES()
    assert list(spec["required"]) == ["image", "reference", "strength"] and list(spec["optional"]) == ["mask", "enabled", "measure_in_mask"]; n += 1
    assert m.SYColourMatch.RETURN_NAMES == ("image", "info"); n += 1
    try:
        import torch
    except ImportError:
        torch = None
    if torch is not None:
        img = torch.rand(1, 8, 8, 3)
        ref = torch.rand(1, 8, 8, 3)
        info = m.SYColourMatch().run(img, ref, 0.4)[1]
        assert "mix 40%" in info and "strength" not in info, info; n += 1
        assert "mix 100%" in m.SYColourMatch().run(img, ref, 1.0)[1]; n += 1
        # a pale patch on black, reference a dark patch on the same black: only measuring inside the mask reaches the dark patch
        mask = torch.zeros(1, 8, 8)
        mask[:, 2:6, 2:6] = 1.0
        pale, dark = torch.zeros(1, 8, 8, 3), torch.zeros(1, 8, 8, 3)
        pale[:, 2:6, 2:6, :] = 0.9
        dark[:, 2:6, 2:6, :] = 0.3
        inside = m.SYColourMatch().run(pale, dark, 1.0, mask, True, True)[0]
        assert near(float(inside[0, 3, 3, 0]), 0.3, 1e-4), float(inside[0, 3, 3, 0]); n += 1
        assert near(float(inside[0, 0, 0, 0]), 0.0, 1e-4); n += 1
        whole = m.SYColourMatch().run(pale, dark, 1.0, mask)[0]
        assert float(whole[0, 3, 3, 0]) > 0.25; n += 1
        empty = m.SYColourMatch().run(pale, dark, 1.0, torch.zeros(1, 8, 8), True, True)[0]
        assert torch.equal(empty, pale); n += 1
        small = torch.zeros(1, 4, 4)
        small[:, 1:3, 1:3] = 1.0
        assert near(float(m.SYColourMatch().run(pale, dark, 1.0, small, True, True)[0][0, 3, 3, 0]), 0.3, 1e-3); n += 1
    return n
