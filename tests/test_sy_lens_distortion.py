import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_lens_distortion as m
import _sy_ae_common as ae


def run():
    n = 0
    # amount 0: every radius is unchanged
    for r in (0.0, 0.3, 1.0):
        assert m.radial_scale(r, 0.0) == r
        n += 1
    # centre never moves
    assert m.radial_scale(0.0, 1.0) == 0.0 and m.radial_scale(0.0, -1.0) == 0.0
    n += 1
    # barrel reads closer to the centre, pincushion further out
    assert m.radial_scale(0.8, 0.5) < 0.8 < m.radial_scale(0.8, -0.5)
    n += 1
    # the warp never folds back on itself (stays rising) over the whole range
    for a in (-1.0, -0.5, 0.0, 0.5, 1.0):
        prev = -1.0
        for i in range(0, 101):
            v = m.radial_scale(i / 100.0, a)
            assert v > prev
            prev = v
    n += 5
    # refusals
    try:
        m.radial_scale(0.5, 2.0)
        raise SystemExit("expected ValueError")
    except ValueError as e:
        assert "amount" in str(e)
    try:
        ae.check_shape((3, 3, 3, 3, 3))
        raise SystemExit("expected ValueError")
    except ValueError:
        pass
    n += 2
    edge = m.SYLensDistortion.INPUT_TYPES()["required"]["edge"]
    assert edge[0] == ["stretch", "black", "mirror"] and edge[1]["default"] == "stretch"
    n += 1
    return n
