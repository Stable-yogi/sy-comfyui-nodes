import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_overlay_preview as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def run():
    n = 0
    img = [[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]]
    mask = [[1.0, 0.0]]
    out = m.overlay(img, mask, 255, 0, 0, 0.5)
    assert abs(out[0][0][0] - 0.5) < 1e-9 and out[0][0][1] == 0.0 and out[0][1] == [0.0, 0.0, 0.0]
    assert m.overlay(img, mask, 255, 0, 0, 0.0) == img
    assert m.overlay(img, mask, 255, 255, 255, 1.0)[0][0] == [1.0, 1.0, 1.0]
    n += 3
    soft = m.overlay(img, [[0.5, 0.0]], 0, 255, 0, 1.0)
    assert abs(soft[0][0][1] - 0.5) < 1e-9
    n += 1
    img4 = [[[0.2, 0.2, 0.2, 0.7]]]
    assert m.overlay(img4, [[1.0]], 0, 0, 0, 1.0)[0][0][3] == 0.7  # alpha untouched
    n += 1
    big = m.overlay(img, [[1.0], [1.0]], 255, 0, 0, 1.0)  # mask of other size is stretched
    assert big[0][1][0] == 1.0
    n += 1
    assert raises(m.overlay, img, mask, 255, 0, 0, 2.0) and raises(m.overlay, img, mask, 300, 0, 0, 0.5)
    n += 1
    return n
