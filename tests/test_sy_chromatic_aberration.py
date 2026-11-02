import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_chromatic_aberration as m


def bad(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.channel_scales(0, 100) == (1.0, 1.0); n += 1
    r, b = m.channel_scales(4, 100)
    assert abs(r - 1.04) < 1e-9 and abs(b - 0.96) < 1e-9; n += 1
    r2, b2 = m.channel_scales(8, 100)
    assert r2 > r and b2 < b; n += 1
    assert m.channel_scales(1000, 10)[1] > 0; n += 1
    assert bad(m.channel_scales, -1, 10); n += 1
    assert bad(m.channel_scales, 1, 0); n += 1
    rad = m.far_corner_radius(100, 100, 0.5, 0.5)
    assert abs(rad - 70.7106781) < 1e-4; n += 1
    assert m.far_corner_radius(100, 100, 0.0, 0.0) > rad; n += 1
    assert m.SYChromaticAberration.RETURN_NAMES == ("image",); n += 1
    return n  # checks
