import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import _sy_mask_math as mm


def run():
    n = 0
    assert mm.mask_bbox([[0.0, 0.0], [0.0, 0.0]]) is None  # empty mask
    assert mm.mask_bbox([[0.0, 1.0], [0.0, 0.0]]) == (1, 0, 1, 1)
    assert mm.mask_bbox([[1.0, 0.0], [0.0, 1.0]]) == (0, 0, 2, 2)
    n += 3
    k = mm.gaussian_kernel(3)
    assert len(k) == 7 and abs(sum(k) - 1.0) < 1e-9 and k[3] == max(k) and mm.gaussian_kernel(0) == [1.0]
    n += 1
    assert mm.disc_half_widths(2) == {-2: 0, -1: 1, 0: 2, 1: 1, 2: 0}
    n += 1
    s = {"left": True, "right": False, "top": False, "bottom": False}
    f = mm.edge_fade_list(4, 1, 3, s)
    assert f[0][0] == 0.25 and f[0][3] == 1.0 and f[0][1] < f[0][2]
    assert mm.edge_fade_list(3, 3, 0, {"left": True, "right": True, "top": True, "bottom": True}) == [[1.0] * 3] * 3
    n += 2
    s_all = mm.open_sides({"x": 0, "y": 2, "w": 5, "h": 3, "image_w": 5, "image_h": 8})
    assert s_all == {"left": False, "top": True, "right": False, "bottom": True}
    n += 1
    base = [[[0.0] * 3 for _ in range(4)] for _ in range(4)]
    try:
        mm.paste_list(base, [[[1.0] * 3] * 3] * 3, None, 2, 2)  # crop sticks out of the image
        raise SystemExit("paste beyond the image must raise")
    except ValueError:
        pass
    n += 1
    return n
