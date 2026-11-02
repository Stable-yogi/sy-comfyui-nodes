import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_selective_colour as m
import _sy_ae_common as ae


def run():
    n = 0
    # normal: centre is fully in, far away is out
    assert m.hue_weight(120, 120, 40, 0.5) == 1.0
    assert m.hue_weight(300, 120, 40, 0.5) == 0.0
    n += 2
    # softness 0: hard edge; softness 1: fades from the centre
    assert m.hue_weight(139, 120, 40, 0.0) == 1.0 and m.hue_weight(141, 120, 40, 0.0) == 0.0
    assert 0.0 < m.hue_weight(110, 120, 40, 1.0) < 1.0
    n += 2
    # fade is smooth and never rises with distance
    prev = 1.0
    for d in range(0, 40):
        w = m.hue_weight(120 + d, 120, 60, 1.0)
        assert 0.0 <= w <= prev + 1e-12
        prev = w
    n += 1
    # circular: wraps at 360
    assert m.hue_weight(355, 5, 40, 0.5) == 1.0
    assert abs(m.hue_weight(350, 10, 60, 0.5) - m.hue_weight(10, 350, 60, 0.5)) < 1e-12
    assert m.hue_distance(359, 1) == 2.0
    n += 3
    # refusals
    for bad in ((100, 120, 400, 0.5), (100, 120, 40, 1.5)):
        try:
            m.hue_weight(*bad)
            raise SystemExit("expected ValueError")
        except ValueError as e:
            assert str(e)
    n += 2
    try:
        ae.check_shape((8,))
        raise SystemExit("expected ValueError")
    except ValueError:
        pass
    n += 1
    d = m.SYSelectiveColour.INPUT_TYPES()["required"]
    assert d["hue_centre"][1]["default"] == 120.0 and d["hue_width"][1]["default"] == 40.0
    n += 1
    return n
