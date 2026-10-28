import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_apply_mask_to_image as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def run():
    n = 0
    img = [[[0.8, 0.6, 0.4], [0.8, 0.6, 0.4]]]
    mask = [[1.0, 0.0]]
    a = m.apply_mask(img, mask, "alpha")
    assert len(a[0][0]) == 4 and a[0][0][3] == 1.0 and a[0][1][3] == 0.0 and a[0][0][:3] == [0.8, 0.6, 0.4]
    b = m.apply_mask(img, mask, "black")
    assert b[0][0] == [0.8, 0.6, 0.4] and b[0][1] == [0.0, 0.0, 0.0] and len(b[0][1]) == 3
    g = m.apply_mask(img, mask, "gray")
    assert g[0][1] == [0.5, 0.5, 0.5]
    n += 3
    o = m.apply_mask(img, mask, "black", "outside")
    assert o[0][0] == [0.0, 0.0, 0.0] and o[0][1] == [0.8, 0.6, 0.4]
    n += 1
    half = m.apply_mask(img, [[0.5, 0.5]], "black")
    assert abs(half[0][0][0] - 0.4) < 1e-9
    n += 1
    img4 = [[[0.1, 0.1, 0.1, 0.5]]]
    assert m.apply_mask(img4, [[0.5]], "alpha")[0][0][3] == 0.25  # alpha is multiplied
    assert m.apply_mask(img4, [[0.0]], "gray")[0][0] == [0.5, 0.5, 0.5, 0.5]
    n += 2
    assert len(m.apply_mask(img, [[1.0], [0.0]], "alpha")) == 1  # mask stretched to the picture
    n += 1
    assert raises(m.apply_mask, img, mask, "pink") and raises(m.apply_mask, img, mask, "alpha", "both")
    n += 1
    return n
