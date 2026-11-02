import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_distance_falloff as m


def run():
    n = 0
    for c in m.CURVES:
        assert m.falloff(0, c) == 1.0
        assert m.falloff(1, c) == 0.0
        assert m.falloff(2.5, c) == 0.0 and m.falloff(-1, c) == 1.0
        n += 3
    assert m.falloff(0.5, "linear") == 0.5
    assert abs(m.falloff(0.5, "smooth") - 0.5) < 1e-9
    assert m.falloff(0.5, "sharp") == 0.25
    n += 3
    # falloff goes down as t goes up
    for c in m.CURVES:
        vals = [m.falloff(i / 10.0, c) for i in range(11)]
        assert all(vals[i] >= vals[i + 1] for i in range(10))
        n += 1
    assert m.outside_value(0, 10, "linear") == 1.0
    assert 0.0 < m.outside_value(10, 10, "linear") < 0.1
    assert m.inside_value(1, 10, "linear") == 0.0
    assert m.inside_value(11, 10, "linear") == 1.0
    n += 4
    for bad in ((0, "outside", "linear"), (300, "outside", "linear"), (5, "left", "linear"), (5, "both", "wavy")):
        try:
            m.check_args(*bad)
            raise SystemExit("bad args must raise")
        except ValueError as e:
            assert str(e)
        n += 1
    try:
        m.falloff(0.5, "wavy")
        raise SystemExit("bad curve must raise")
    except ValueError as e:
        assert "curve must be" in str(e)
    n += 1
    assert m.SYMaskDistanceFalloff.RETURN_TYPES == ("MASK",)
    assert list(m.SYMaskDistanceFalloff.INPUT_TYPES()["required"]) == ["mask", "distance", "side", "curve"]
    n += 2
    return n
