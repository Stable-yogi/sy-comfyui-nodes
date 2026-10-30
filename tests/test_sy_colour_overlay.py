import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_colour_overlay as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def near(a, b, eps=1e-9):
    return abs(a - b) < eps


def run():
    n = 0
    assert near(m.overlay_value(0.3, 0.8, "normal"), 0.8); n += 1
    assert near(m.overlay_value(0.5, 0.4, "multiply"), 0.2); n += 1
    assert near(m.overlay_value(0.5, 0.4, "screen"), 1 - 0.5 * 0.6); n += 1
    assert near(m.overlay_value(0.25, 0.6, "overlay"), 2 * 0.25 * 0.6); n += 1
    assert near(m.overlay_value(0.75, 0.6, "overlay"), 1 - 2 * 0.25 * 0.4); n += 1
    assert near(m.overlay_value(0.5, 0.6, "overlay"), 1 - 2 * 0.5 * 0.4); n += 1
    assert near(m.overlay_value(1.0, 0.3, "multiply"), 0.3); n += 1
    assert near(m.overlay_value(0.0, 0.3, "screen"), 0.3); n += 1
    msg = raises(m.overlay_value, 0.5, 0.5, "burn")
    assert msg and "mode" in msg; n += 1
    base = (0.2, 0.4, 0.6)
    col = (1.0, 0.0, 0.5)
    assert m.overlay_pixel(base, col, 0.0, "normal") == base; n += 1
    assert m.overlay_pixel(base, col, 1.0, "normal") == col; n += 1
    p = m.overlay_pixel(base, col, 0.5, "normal")
    assert near(p[0], 0.6) and near(p[1], 0.2) and near(p[2], 0.55); n += 1
    assert m.overlay_pixel(base, col, 1.0, "normal", 0.0) == base; n += 1
    p = m.overlay_pixel(base, col, 1.0, "normal", 0.5)
    assert near(p[0], 0.6); n += 1
    msg = raises(m.overlay_pixel, base, col, 1.5, "normal")
    assert msg and "opacity" in msg; n += 1
    assert m.check_mask_shape((1, 4, 6), (2, 4, 6, 3)) is None; n += 1
    assert m.check_mask_shape((2, 4, 6), (2, 4, 6, 4)) is None; n += 1
    assert m.check_mask_shape((4, 6), (1, 4, 6, 3)) is None; n += 1
    msg = raises(m.check_mask_shape, (1, 5, 6), (1, 4, 6, 3))
    assert msg and "differs" in msg and "image size" in msg; n += 1
    msg = raises(m.check_mask_shape, (3, 4, 6), (2, 4, 6, 3))
    assert msg and "batch" in msg; n += 1
    assert raises(m.check_mask_shape, (1, 1, 4, 6), (1, 4, 6, 3)); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYColourOverlay"] == "Colour Overlay SY"; n += 1
    assert m.DEFAULT_COLOUR.startswith("#") and len(m.DEFAULT_COLOUR) == 7; n += 1
    return n
