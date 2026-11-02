import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_seamless_tile_blend as m


def refuses(fn, *args):
    try:
        fn(*args)
    except ValueError as e:
        return len(str(e)) > 10
    return False


def run():
    n = 0
    assert m.seam_weight(0, 100, 0.25) == 0.0; n += 1
    assert m.seam_weight(99, 100, 0.25) == 0.0; n += 1
    assert m.seam_weight(25, 100, 0.25) == 1.0; n += 1
    assert m.seam_weight(50, 100, 0.25) == 1.0; n += 1
    assert abs(m.seam_weight(5, 100, 0.25) - 0.2) < 1e-9; n += 1
    assert m.seam_weight(10, 100, 0.25) < m.seam_weight(20, 100, 0.25); n += 1
    assert m.seam_weight(30, 100, 0.25) == m.seam_weight(69, 100, 0.25); n += 1
    assert m.seam_weight(1, 2, 0.5) == 0.0 and m.seam_weight(0, 2, 0.05) == 0.0; n += 1
    w = m.weights_1d(10, 0.5)
    assert len(w) == 10 and w[0] == 0.0 and max(w) <= 1.0 and w == w[::-1]; n += 1
    assert refuses(m.seam_weight, 0, 1, 0.25); n += 1
    assert refuses(m.seam_weight, 0, 10, 0.6); n += 1
    assert refuses(m.seam_weight, 10, 10, 0.25); n += 1
    assert m.check_settings(0.05, "vertical") is None; n += 1
    assert m.check_settings(0.5, "horizontal") is None; n += 1
    assert refuses(m.check_settings, 0.04, "both"); n += 1
    assert refuses(m.check_settings, 0.51, "both"); n += 1
    assert refuses(m.check_settings, 0.25, "diagonal"); n += 1
    assert m.SYSeamlessTileBlend.CATEGORY == "SY/Image"; n += 1
    return n
