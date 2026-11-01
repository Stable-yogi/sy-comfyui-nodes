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
    _k = [0]
    def _c(cond, msg="d3 check failed"):
        _k[0] += 1
        if not cond:
            raise AssertionError(msg)
    def _r(fn, *a):
        _k[0] += 1
        try:
            fn(*a)
        except ValueError as e:
            return str(e)
        raise AssertionError("expected ValueError for %r" % (a,))
    i1 = m.overlay_info(64, 32, 64, 32, 1, 1, 512, 2048)
    _c("25.0%" in i1 and "stretched" not in i1 and "batch" not in i1)
    _c("stretched to the picture size 64x32" in m.overlay_info(64, 32, 8, 8, 1, 1, 10, 2048))
    _c("repeated or cut" in m.overlay_info(64, 32, 64, 32, 4, 2, 10, 2048))
    _c("empty" in m.overlay_info(64, 32, 64, 32, 1, 1, 0, 2048))
    _c("flipped" in m.overlay_info(64, 32, 64, 32, 1, 1, 5, 2048, True))
    _c(m.SYMaskOverlayPreview.RETURN_NAMES == ("image", "info"))
    _c(list(m.SYMaskOverlayPreview.INPUT_TYPES()["required"])[:2] == ["image", "mask"] and "invert_mask" in m.SYMaskOverlayPreview.INPUT_TYPES()["optional"])
    return (n) + _k[0]
