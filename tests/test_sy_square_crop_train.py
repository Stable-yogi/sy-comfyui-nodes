import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_square_crop_train as m


def run():
    assert m.centre_square(100, 100) == (0, 0, 100)
    assert m.centre_square(200, 100) == (50, 0, 100)
    assert m.centre_square(100, 200) == (0, 50, 100)
    assert m.centre_square(101, 100) == (0, 0, 100)             # odd leftover: extra pixel is cut from the right
    assert m.centre_square(105, 100) == (2, 0, 100)
    assert m.centre_square(1, 1) == (0, 0, 1)
    assert m.centre_square(1, 7) == (0, 3, 1)
    for bad in ((0, 5), (5, 0), (-1, 5)):
        try:
            m.centre_square(*bad)
            raise SystemExit("bad size must raise")
        except ValueError:
            pass
    assert m.METHODS[0] == "area"
    assert m.SYSquareCropTrain.RETURN_TYPES[:1] == ("IMAGE",)
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
    _c(m.square_box(1000, 600, "centre") == m.centre_square(1000, 600) == (200, 0, 600))
    _c(m.square_box(600, 1000, "top") == (0, 0, 600) and m.square_box(600, 1000, "bottom") == (0, 400, 600))
    _c(m.square_box(1000, 600, "left") == (0, 0, 600) and m.square_box(1000, 600, "right") == (400, 0, 600))
    _c(m.square_box(1000, 600, "top") == (200, 0, 600) and m.square_box(600, 1000, "left") == (0, 200, 600))
    _c(m.square_box(1000, 600, "top_left") == (0, 0, 600) and m.square_box(600, 1000, "top_left") == (0, 0, 600))
    _c(m.square_box(512, 512, "bottom") == (0, 0, 512))
    _r(m.square_box, 10, 10, "middle")
    _i = m.crop_info(1000, 600, 512, "area", "centre", 3)
    _c("3 pictures of 1000x600" in _i and "600x600 square" in _i and "512x512 with area" in _i and "enlarged" not in _i)
    _c("enlarged x2.0" in m.crop_info(500, 300, 600, "bicubic"))
    _c("already the right size" in m.crop_info(1000, 512, 512, "area"))
    _c(m.SYSquareCropTrain.RETURN_NAMES == ("images", "info") and "anchor" in m.SYSquareCropTrain.INPUT_TYPES()["optional"])
    return (12) + _k[0]
