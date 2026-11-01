import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_crop_percent as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    assert m.crop_box(100, 50, 0, 0, 0, 0) == (0, 0, 100, 50); n += 1
    assert m.crop_box(100, 50, 10, 20, 0, 0) == (10, 0, 80, 50); n += 1
    assert m.crop_box(100, 50, 0, 0, 10, 40) == (0, 5, 100, 30); n += 1
    assert m.crop_box(101, 99, 10, 10, 10, 10) == (10, 10, 91, 89); n += 1  # odd sizes
    assert m.crop_box(1, 1, 0, 0, 0, 0) == (0, 0, 1, 1); n += 1
    assert m.crop_box(1, 1, 49.9, 49.9, 49.9, 49.9) == (0, 0, 1, 1); n += 1
    assert m.crop_box(1, 100, 0, 0, 25, 25) == (0, 25, 1, 75); n += 1
    assert m.crop_box(100, 1, 25, 25, 0, 0) == (25, 0, 75, 1); n += 1
    x0, y0, x1, y1 = m.crop_box(3, 3, 49.9, 49.9, 0, 0)
    assert x1 - x0 >= 1; n += 1
    assert m.crop_box(7, 5, 15, 15, 30, 30) == (1, 2, 6, 3); n += 1
    msg = raises(m.crop_box, 2, 100, 49.9, 49.9, 0, 0)
    assert msg is None or "width" in msg; n += 1  # 2 px at 49.9 percent rounds to 1 pixel each side: empty
    msg = raises(m.crop_box, 3, 100, 49.9, 49.9, 0, 0)
    assert msg is None; n += 1
    msg = raises(m.crop_box, 100, 100, 50, 0, 0, 0)
    assert msg and "left" in msg; n += 1
    msg = raises(m.crop_box, 100, 100, 0, 0, -1, 0)
    assert msg and "top" in msg; n += 1
    assert raises(m.crop_box, 0, 10, 0, 0, 0, 0); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYCropPercent"] == "Crop Percent SY"; n += 1
    assert m.SYCropPercent.CATEGORY == "SY/Resize"; n += 1
    return n + _extra(m)


def _extra(m):
    n = 0
    def ok(c):
        assert c
        return 1
    def rs(fn, *a, **k):
        try:
            fn(*a, **k)
        except ValueError as e:
            return str(e)
        return None
    n += ok(m.crop_box(100, 50, 0, 0, 0, 0, 1) == m.crop_box(100, 50, 0, 0, 0, 0))
    n += ok((lambda b: (b[2] - b[0]) % 8 == 0 and (b[3] - b[1]) % 8 == 0)(m.crop_box(1000, 700, 10, 10, 10, 10, 8)))
    n += ok(m.crop_box(100, 100, 0, 0, 0, 0, 64) == (18, 18, 82, 82))
    n += ok('less than one multiple' in rs(m.crop_box, 100, 100, 40, 40, 0, 0, 64))
    n += ok(rs(m.crop_box, 100, 100, 0, 0, 0, 0, 0) is not None)
    n += ok(m.crop_info(100, 50, (0, 0, 100, 50)) == 'nothing cropped, the picture stays 100x50')
    n += ok(m.crop_info(100, 50, (10, 0, 90, 50)).startswith('cropped 100x50 -> 80x50'))
    n += ok('multiple of 8' in m.crop_info(100, 50, (10, 0, 90, 48), 8))
    n += ok(m.SYCropPercent.RETURN_TYPES[-1] == 'STRING')
    return n
