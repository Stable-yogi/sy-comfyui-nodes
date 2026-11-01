import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_crop_to_aspect as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def near(a, b, eps=1e-6):
    return abs(a - b) < eps


def run():
    n = 0
    assert m.crop_box(1000, 1000, 16, 9)[2:] == (1000, 562); n += 1
    assert m.crop_box(1920, 1080, 1, 1) == (420, 0, 1080, 1080); n += 1
    x, y, w, h = m.crop_box(1920, 1080, 1, 1, -1, 0)
    assert x == 0 and w == 1080; n += 1
    x, y, w, h = m.crop_box(1920, 1080, 1, 1, 1, 0)
    assert x == 840 and x + w == 1920; n += 1
    assert m.crop_box(1000, 2000, 1, 1, 0, 1) == (0, 1000, 1000, 1000); n += 1
    assert m.crop_box(1600, 900, 16, 9) == (0, 0, 1600, 900); n += 1
    x, y, w, h = m.crop_box(1000, 1000, 5, 1, 5, -5)
    assert (w, h) == (1000, 200) and y == 0; n += 1
    assert raises(m.crop_box, 100, 100, 0, 9); n += 1
    assert raises(m.crop_box, 0, 100, 1, 1); n += 1
    assert m.snap_size(1080, 607, 1) == (1080, 607); n += 1
    assert m.snap_size(1080, 607, 8) == (1080, 600); n += 1
    assert m.snap_size(5, 3, 8) == (5, 3); n += 1
    assert m.snap_size(70, 40, 64) == (64, 40); n += 1
    try:
        m.snap_size(10, 10, 0)
        raise SystemExit("expected ValueError")
    except ValueError as e:
        assert "multiple_of" in str(e); n += 1
    assert "1920x1080 -> 1080x1080" in m.crop_info(1920, 1080, 420, 0, 1080, 1080); n += 1
    assert m.SYCropToAspect.RETURN_NAMES == ("image", "width", "height", "info"); n += 1
    return n
