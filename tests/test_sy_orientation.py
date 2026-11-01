import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_orientation as m


class _Fake:
    """Stands in for an IMAGE tensor: only .shape is read."""

    def __init__(self, shape):
        self.shape = shape


def run():
    assert m.classify(1024, 512) == "landscape"
    assert m.classify(512, 1024) == "portrait"
    assert m.classify(512, 512) == "square"
    assert m.classify(1000, 990, 0) == "landscape"
    assert m.classify(1000, 990, 1.0) == "square"
    assert m.classify(990, 1000, 2) == "square"
    assert m.classify(1000, 900, 5) == "landscape"
    for bad in ((0, 5, 0), (5, 5, -1), (5, 5, 101)):
        try:
            m.classify(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError:
            pass
    assert m.image_size(_Fake((2, 480, 640, 3))) == (640, 480)
    try:
        m.image_size(_Fake((480, 640, 3)))
        raise SystemExit("bad shape must raise")
    except ValueError:
        pass
    assert m.SYOrientation().run(_Fake((1, 480, 640, 3)))[:4] == ("landscape", True, 640, 480)
    assert m.SYOrientation().run(_Fake((1, 640, 480, 3)))[1] is False
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYOrientation"] == "Orientation SY"
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
    _i = m.orientation_info("landscape", 1920, 1080)
    _c("Landscape picture, 1920x1080" in _i and "16:9" in _i and "2.07 megapixels" in _i and "batch" not in _i)
    _c("batch has 3 pictures" in m.orientation_info("portrait", 512, 768, 3) and "2:3" in m.orientation_info("portrait", 512, 768, 3))
    _c(m.SYOrientation.RETURN_NAMES[:4] == ("orientation", "is_landscape", "width", "height") and m.SYOrientation.RETURN_NAMES[4:] == ("aspect_ratio", "info"))
    _c(len(m.SYOrientation.RETURN_TYPES) == len(m.SYOrientation.RETURN_NAMES) == 6)
    return (16) + _k[0]
