import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_gradient_image as m
import _sy_hexcolour as hx


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
    assert near(m.gradient_t(0, 0, 4, 1, "linear", 0), 0.125); n += 1
    assert near(m.gradient_t(3, 0, 4, 1, "linear", 0), 0.875); n += 1
    assert near(m.gradient_t(0, 0, 1, 4, "linear", 90), 0.125); n += 1
    assert near(m.gradient_t(0, 3, 1, 4, "linear", 90), 0.875); n += 1
    assert near(m.gradient_t(3, 0, 4, 1, "linear", 180), 0.125); n += 1
    assert near(m.gradient_t(0, 3, 1, 4, "linear", 270), 0.125); n += 1
    assert near(m.gradient_t(0, 0, 4, 1, "linear", -360), 0.125); n += 1
    assert near(m.gradient_t(0, 0, 1, 1, "linear", 33), 0.5); n += 1
    assert near(m.gradient_t(0, 0, 1, 1, "radial", 0), 0.0); n += 1
    assert m.gradient_t(0, 0, 100, 100, "linear", 45) < 0.01; n += 1
    assert m.gradient_t(99, 99, 100, 100, "linear", 45) > 0.99; n += 1
    assert m.gradient_t(49, 49, 100, 100, "radial", 0) < 0.02; n += 1
    assert m.gradient_t(0, 0, 100, 100, "radial", 0) > 0.98; n += 1
    assert 0.0 <= m.gradient_t(0, 0, 5, 3, "radial", 0) <= 1.0; n += 1
    assert m.gradient_pixel(0.0, (0, 0, 0), (1, 1, 1)) == (0, 0, 0); n += 1
    assert m.gradient_pixel(0.5, (0, 0, 0), (1, 1, 1)) == (0.5, 0.5, 0.5); n += 1
    assert raises(m.gradient_t, 0, 0, 0, 5, "linear", 0); n += 1
    assert raises(m.gradient_t, 0, 0, 5, 5, "conical", 0); n += 1
    assert hx.parse_hex(m.DEFAULT_A) == hx.parse_hex("1b1b2f") and m.DEFAULT_B == "#f5d58a"; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYGradientImage"] == "Gradient Image SY"; n += 1
    assert m.ease_t(0.0, "smooth") == 0.0 and m.ease_t(1.0, "smooth") == 1.0 and near(m.ease_t(0.5, "smooth"), 0.5); n += 1
    assert m.ease_t(0.25, "smooth") < 0.25 and m.ease_t(0.75, "smooth") > 0.75; n += 1
    assert m.ease_t(0.3, "linear") == 0.3 and m.ease_t(-1.0, "linear") == 0.0 and m.ease_t(2.0, "smooth") == 1.0; n += 1
    assert raises(m.ease_t, 0.5, "wavy"); n += 1
    assert m.pick_size(512, 256) == (512, 256) and m.pick_size(512, 256, 1024, 768) == (1024, 768); n += 1
    assert "more than 8192" in raises(m.pick_size, 9000, 10); n += 1
    assert raises(m.pick_size, 0, 10) and raises(m.pick_size, 10, 10, 0, 5); n += 1
    t = m.gradient_info(512, 256, "linear", 90.0, "#000", "#fff", "smooth", 2, True)
    assert "512x256" in t and "at 90 degrees" in t and "smooth linear" in t and "2 picture(s)" in t and "connected picture" in t; n += 1
    assert "from the centre outward" in m.gradient_info(8, 8, "radial", 0.0, "a", "b", "linear", 1, False); n += 1
    assert m.SYGradientImage.RETURN_NAMES == ("image", "mask", "info"); n += 1
    assert list(m.SYGradientImage.INPUT_TYPES()["optional"]) == ["size_from", "ease"]; n += 1
    return n
