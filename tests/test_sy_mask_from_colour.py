import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_from_colour as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def dot(h, w, x, y, v=1.0):
    r = [[0.0] * w for _ in range(h)]
    r[y][x] = v
    return r


def run():
    n = 0
    img = [[[0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.9, 0.0]]]
    assert m.colour_mask(img, 0, 255, 0, 0) == [[1.0, 0.0, 0.0]]
    assert m.colour_mask(img, 0, 255, 0, 30) == [[1.0, 0.0, 1.0]]  # 0.9*255 = 229.5, off by 25.5
    assert m.colour_mask(img, 0, 255, 0, 255) == [[1.0, 1.0, 1.0]]
    n += 3
    img4 = [[[0.0, 1.0, 0.0, 0.5]]]  # alpha channel ignored
    assert m.colour_mask(img4, 0, 255, 0, 0) == [[1.0]]
    n += 1
    assert raises(m.colour_mask, img, 300, 0, 0, 0) and raises(m.colour_mask, img, 0, 0, 0, 999)
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
    _c(m.pick_colour(1, 2, 3) == (1, 2, 3))
    _c(m.pick_colour(1, 2, 3, "") == (1, 2, 3))
    _c(m.pick_colour(1, 2, 3, "  ") == (1, 2, 3))
    _c(m.pick_colour(0, 0, 0, "#ff8800") == (255, 136, 0))
    _c(m.pick_colour(0, 0, 0, "f00") == (255, 0, 0))
    _c("hex_colour" in _r(m.pick_colour, 0, 0, 0, "zzz"))
    _c("empty" in m.colour_info(0, 100, (0, 255, 0), 20))
    _c("whole picture" in m.colour_info(100, 100, (0, 255, 0), 20))
    _c("25.0%" in m.colour_info(25, 100, (1, 2, 3), 5))
    _c("flipped" in m.colour_info(25, 100, (1, 2, 3), 5, True))
    _c("empty" not in m.colour_info(25, 100, (1, 2, 3), 5))
    _c(m.SYMaskFromColour.RETURN_NAMES == ("mask", "info") and len(m.SYMaskFromColour.RETURN_TYPES) == 2)
    _c(list(m.SYMaskFromColour.INPUT_TYPES()["required"])[:5] == ["image", "red", "green", "blue", "tolerance"])
    return (n) + _k[0]
