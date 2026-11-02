import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_radial_zoom_blur as m


def refuses(fn, *args):
    try:
        fn(*args)
    except ValueError as e:
        return len(str(e)) > 10
    return False


def run():
    n = 0
    s = m.zoom_scales(0.1, 5)
    assert len(s) == 5 and s[0] == 1.0 and abs(s[-1] - 0.9) < 1e-9; n += 1
    assert all(s[i] > s[i + 1] for i in range(4)); n += 1
    assert m.zoom_scales(0.0, 4) == [1.0] * 4; n += 1
    assert abs(m.zoom_scales(0.5, 32)[-1] - 0.5) < 1e-9 and len(m.zoom_scales(0.5, 32)) == 32; n += 1
    assert len(m.zoom_scales(0.2, 2)) == 2; n += 1
    assert refuses(m.zoom_scales, 1.0, 5); n += 1
    assert refuses(m.zoom_scales, -0.1, 5); n += 1
    assert refuses(m.zoom_scales, 0.1, 1); n += 1
    assert m.check_settings(0, 4, 0, 0) is None; n += 1
    assert m.check_settings(0.5, 32, 1, 1) is None; n += 1
    assert refuses(m.check_settings, 0.6, 12, 0.5, 0.5); n += 1
    assert refuses(m.check_settings, 0.1, 3, 0.5, 0.5); n += 1
    assert refuses(m.check_settings, 0.1, 33, 0.5, 0.5); n += 1
    assert refuses(m.check_settings, 0.1, 12, 1.5, 0.5); n += 1
    assert refuses(m.check_settings, 0.1, 12, 0.5, -0.1); n += 1
    assert m.SYRadialZoomBlur.CATEGORY == "SY/Image"; n += 1
    return n
