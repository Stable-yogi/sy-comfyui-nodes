import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_split_toning as m


def _refuses(fn, word, *args):
    try:
        fn(*args)
    except ValueError as e:
        assert word in str(e), str(e)
        return 1
    raise SystemExit("expected ValueError")


def run():
    n = 0
    # normal: the main hues
    for hue, want in ((0, (1, 0, 0)), (120, (0, 1, 0)), (240, (0, 0, 1)), (60, (1, 1, 0)), (180, (0, 1, 1))):
        got = m.hue_to_rgb(hue)
        assert all(abs(a - b) < 1e-9 for a, b in zip(got, want)), (hue, got)
    n += 5
    # edge: 360 wraps to 0
    assert m.hue_to_rgb(360) == m.hue_to_rgb(0)
    n += 1
    # weights: sum to 1, dark is shadow, bright is highlight, smooth and rising
    for luma in (0.0, 0.2, 0.5, 0.8, 1.0):
        for bal in (-1.0, 0.0, 1.0):
            s, h = m.split_weights(luma, bal)
            assert s >= 0 and h >= 0 and s + h <= 1.0 + 1e-12
    n += 1
    s0, h0 = m.split_weights(0.0, 0.0)
    s1, h1 = m.split_weights(1.0, 0.0)
    assert s0 == 1.0 and h0 == 0.0 and s1 == 0.0 and h1 == 1.0
    ms, mh = m.split_weights(0.5, 0.0)
    assert abs(ms - 0.5) < 1e-9
    prev = -1.0
    for i in range(11):
        h = m.split_weights(i / 10.0, 0.0)[1]
        assert h >= prev
        prev = h
    n += 4
    # balance moves the split: + means a mid grey is still mostly shadow, - mostly highlight
    assert m.split_weights(0.5, 1.0)[0] > 0.9 and m.split_weights(0.5, -1.0)[1] > 0.9
    n += 1
    # refusals
    n += _refuses(m.split_weights, "balance", 0.5, 2.0)
    n += _refuses(m.split_weights, "luma", -0.1, 0.0)
    n += _refuses(m.hue_to_rgb, "hue", float("nan"))
    d = m.SYSplitToning.INPUT_TYPES()["required"]
    assert d["shadow_hue"][1]["default"] == 210.0 and d["highlight_hue"][1]["default"] == 40.0
    assert d["shadow_saturation"][1]["default"] == 0.25 and d["strength"][1]["default"] == 1.0 and d["balance"][1]["default"] == 0.0
    n += 1
    return n
