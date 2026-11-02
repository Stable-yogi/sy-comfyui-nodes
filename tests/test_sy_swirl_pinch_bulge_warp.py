import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_swirl_pinch_bulge_warp as m


def _refuses(fn, word):
    try:
        fn()
    except ValueError as e:
        assert word in str(e), str(e)
        return 1
    raise SystemExit("expected ValueError")


def run():
    n = 0
    # normal: swirl angle is biggest at the centre and fades
    a0 = m.warp_scale(0.0, "swirl", 0.6)
    a5 = m.warp_scale(0.5, "swirl", 0.6)
    assert a0 > a5 > 0
    assert abs(m.warp_scale(0.0, "swirl", -0.6) + a0) < 1e-12
    n += 2
    # bulge magnifies (factor below 1) and pinch is the opposite
    assert m.warp_scale(0.0, "bulge", 1.0) < 1.0 < m.warp_scale(0.0, "pinch", 1.0)
    n += 1
    # edge: at and beyond the radius there is no change
    for mode in m.MODES:
        same = 0.0 if mode == "swirl" else 1.0
        assert m.warp_scale(1.0, mode, 2.0) == same and m.warp_scale(3.0, mode, -2.0) == same
        n += 1
    # smooth: just inside the radius the change is tiny (no hard seam)
    assert abs(m.warp_scale(0.999, "swirl", 2.0)) < 1e-4
    assert abs(m.warp_scale(0.999, "bulge", 2.0) - 1.0) < 1e-3
    n += 2
    # strength 0 does nothing
    assert m.warp_scale(0.3, "swirl", 0.0) == 0.0 and m.warp_scale(0.3, "pinch", 0.0) == 1.0
    n += 1
    # factor never reaches zero at the strongest setting
    assert m.warp_scale(0.0, "bulge", 2.0) > 0.0
    n += 1
    # refusals
    n += _refuses(lambda: m.warp_scale(0.5, "twirl", 0.5), "mode")
    n += _refuses(lambda: m.warp_scale(0.5, "swirl", 3.0), "strength")
    n += _refuses(lambda: m.warp_scale(-1.0, "swirl", 0.5), "r_norm")
    n += _refuses(lambda: m.warp_tensor(None, "spin", 0.5, 0.5, 0.5, 0.5, "stretch"), "mode")
    n += _refuses(lambda: m.warp_tensor(None, "swirl", 0.5, 0.5, 0.5, 0.5, "wrap"), "edge")
    n += _refuses(lambda: m.warp_tensor(None, "swirl", 0.5, 2.0, 0.5, 0.5, "stretch"), "radius")
    d = m.SYSwirlPinchBulgeWarp.INPUT_TYPES()["required"]
    assert d["mode"][1]["default"] == "swirl" and d["strength"][1]["default"] == 0.6 and d["radius"][1]["default"] == 0.5
    n += 1
    return n
