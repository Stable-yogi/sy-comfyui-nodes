import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_glitch_slices as m


def refuses(fn, *args):
    try:
        fn(*args)
    except ValueError as e:
        return len(str(e)) > 10
    return False


def run():
    n = 0
    p = m.plan_slices(100, 12, 10, 7)
    assert len(p) == 12 and p[0][0] == 0 and p[-1][1] == 100; n += 1
    assert all(p[i][1] == p[i + 1][0] for i in range(len(p) - 1)); n += 1
    assert all(t < b for t, b, _ in p); n += 1
    assert all(-10 <= s <= 10 for _, _, s in p); n += 1
    assert m.plan_slices(100, 12, 10, 7) == p; n += 1
    assert m.plan_slices(100, 12, 10, 8) != p; n += 1
    assert m.plan_slices(50, 1, 5, 0) == [(0, 50, m.plan_slices(50, 1, 5, 0)[0][2])]; n += 1
    assert all(s == 0 for _, _, s in m.plan_slices(40, 5, 0, 3)); n += 1
    assert len(m.plan_slices(3, 60, 4, 1)) == 3; n += 1
    assert len(m.plan_slices(1, 5, 4, 1)) == 1; n += 1
    assert refuses(m.plan_slices, 0, 5, 1, 0); n += 1
    assert refuses(m.plan_slices, 10, 0, 1, 0); n += 1
    assert refuses(m.plan_slices, 10, 3, -1, 0); n += 1
    assert m.check_settings(1, 0, 0) is None; n += 1
    assert m.check_settings(60, 0.3, 0.05) is None; n += 1
    assert refuses(m.check_settings, 0, 0.1, 0.01); n += 1
    assert refuses(m.check_settings, 61, 0.1, 0.01); n += 1
    assert refuses(m.check_settings, 5, 0.4, 0.01); n += 1
    assert refuses(m.check_settings, 5, 0.1, 0.1); n += 1
    assert m.SYGlitchSlices.CATEGORY == "SY/Image"; n += 1
    return n
