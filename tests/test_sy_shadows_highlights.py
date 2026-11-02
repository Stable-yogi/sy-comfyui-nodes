import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_shadows_highlights as m


def _refuses(fn, word, *args):
    try:
        fn(*args)
    except ValueError as e:
        assert word in str(e), str(e)
        return 1
    raise SystemExit("expected ValueError")


def run():
    n = 0
    # both sliders 0: exactly 1 everywhere (picture unchanged)
    for l in (0.0, 0.1, 0.5, 0.9, 1.0):
        assert abs(m.tone_gain(l, 0.0, 0.0, 0.5) - 1.0) < 1e-4
    n += 5
    # shadows up brightens dark areas, leaves bright ones alone
    assert m.tone_gain(0.05, 0.5, 0.0, 0.5) > 1.5
    assert abs(m.tone_gain(0.9, 0.5, 0.0, 0.5) - 1.0) < 1e-9
    n += 2
    # highlights down darkens bright areas, leaves dark ones alone
    assert m.tone_gain(0.95, 0.0, -0.5, 0.5) < 0.8
    assert abs(m.tone_gain(0.1, 0.0, -0.5, 0.5) - 1.0) < 1e-9
    n += 2
    # negative shadows darkens, positive highlights brightens
    assert m.tone_gain(0.0, -0.5, 0.0, 0.5) < 1.0 and m.tone_gain(1.0, 0.0, 0.5, 0.5) > 1.0
    n += 1
    # wider tonal width reaches further into the mid-tones
    assert m.tone_gain(0.4, 0.5, 0.0, 0.9) > m.tone_gain(0.4, 0.5, 0.0, 0.2)
    n += 1
    # edge: extreme sliders stay finite and not negative
    for s in (-1.0, 1.0):
        for h in (-1.0, 1.0):
            for l in (0.0, 0.5, 1.0):
                g = m.tone_gain(l, s, h, 0.1)
                assert 0.0 <= g < 10.0
    n += 1
    # refusals
    n += _refuses(m.tone_gain, "shadows", 0.5, 1.5, 0.0, 0.5)
    n += _refuses(m.tone_gain, "highlights", 0.5, 0.0, -2.0, 0.5)
    n += _refuses(m.tone_gain, "tonal_width", 0.5, 0.0, 0.0, 0.0)
    n += _refuses(m.tone_gain, "local_luma", 1.5, 0.0, 0.0, 0.5)
    d = m.SYShadowsHighlights.INPUT_TYPES()["required"]
    assert d["shadows"][1]["default"] == 0.3 and d["highlights"][1]["default"] == -0.2 and d["tonal_width"][1]["default"] == 0.5
    assert d["radius"][1]["default"] == 30 and d["colour_keep"][1]["default"] == 0.8
    n += 1
    return n
