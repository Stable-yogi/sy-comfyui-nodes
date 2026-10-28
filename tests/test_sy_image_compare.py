import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_image_compare as m


def solid(h, w, v):
    return [[[v, v, v] for _ in range(w)] for _ in range(h)]


def run():
    a, b = solid(2, 4, 0.2), solid(2, 4, 0.8)
    s = m.compare_images(a, b, "side_by_side")
    assert len(s) == 2 and len(s[0]) == 8 and s[0][0][0] == 0.2 and s[0][7][0] == 0.8
    d = m.compare_images(a, b, "difference")
    assert abs(d[1][3][0] - 0.6) < 1e-9
    bl = m.compare_images(a, b, "blend", 0.5)
    assert abs(bl[0][0][1] - 0.5) < 1e-9
    assert m.compare_images(a, b, "blend", 0.0)[0][0][0] == 0.2
    assert m.compare_images(a, b, "blend", 1.0)[0][0][0] == 0.8
    w = m.compare_images(a, b, "wipe", 0.5)
    assert w[0][1][0] == 0.2 and w[0][2][0] == 0.8
    ck = m.compare_images(a, b, "checker")
    assert ck[0][0][0] == 0.2 and len(ck[0]) == 4
    big = solid(8, 8, 0.2)
    ck2 = m.compare_images(big, solid(8, 8, 0.8), "checker")
    assert ck2[0][0][0] == 0.2 and ck2[0][1][0] == 0.8 and ck2[1][1][0] == 0.2
    small = [[[0.1, 0.1, 0.1], [0.9, 0.9, 0.9]]]  # 1x2
    r = m.resize_nearest(small, 2, 4)
    assert len(r) == 2 and len(r[0]) == 4 and r[0][0][0] == 0.1 and r[1][3][0] == 0.9
    diff_size = m.compare_images(a, small, "difference")
    assert len(diff_size) == 2 and len(diff_size[0]) == 4
    try:
        m.compare_images(a, b, "bogus")
        raise SystemExit("bogus mode must raise")
    except ValueError:
        pass
    assert m.compare_images(a, b, "blend", 5)[0][0][0] == 0.8  # amount is clamped
    return 17  # checks
