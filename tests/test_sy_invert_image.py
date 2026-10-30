import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_invert_image as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def near(a, b, eps=1e-6):
    return abs(a - b) < eps


def run():
    n = 0
    assert m.invert_pixel(0.0, 0.25, 1.0, "rgb") == (1.0, 0.75, 0.0); n += 1
    assert m.invert_pixel(0.5, 0.25, 0.75, "red") == (0.5, 0.25, 0.75); n += 1
    assert m.invert_pixel(0.25, 0.5, 0.75, "red") == (0.75, 0.5, 0.75); n += 1
    assert m.invert_pixel(0.25, 0.5, 0.75, "green") == (0.25, 0.5, 0.75); n += 1
    assert m.invert_pixel(0.25, 0.25, 0.75, "green") == (0.25, 0.75, 0.75); n += 1
    assert m.invert_pixel(0.25, 0.5, 0.25, "blue") == (0.25, 0.5, 0.75); n += 1
    for ch in m.CHANNELS:
        a = m.invert_pixel(0.1, 0.2, 0.3, ch)
        b = m.invert_pixel(a[0], a[1], a[2], ch)
        assert all(near(x, y) for x, y in zip(b, (0.1, 0.2, 0.3))); n += 1
    assert m.invert_pixel(0.5, 0.5, 0.5, "rgb") == (0.5, 0.5, 0.5); n += 1
    msg = raises(m.invert_pixel, 0, 0, 0, "alpha")
    assert msg and "channels" in msg; n += 1
    assert raises(m.invert_pixel, 0, 0, 0, ""); n += 1
    assert raises(m.check_channels, None); n += 1
    assert m.check_channels("rgb") is None; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYInvertImage"] == "Invert Image SY"; n += 1
    assert m.SYInvertImage.CATEGORY.endswith("Image"); n += 1
    return n
