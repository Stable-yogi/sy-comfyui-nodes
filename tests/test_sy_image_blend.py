import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_image_blend as m


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
    assert m.blend_value(0.3, 0.8, "normal") == 0.8; n += 1
    assert near(m.blend_value(0.5, 0.4, "multiply"), 0.2); n += 1
    assert near(m.blend_value(0.5, 0.5, "screen"), 0.75); n += 1
    assert near(m.blend_value(0.25, 0.5, "overlay"), 0.25); n += 1
    assert near(m.blend_value(0.75, 0.5, "overlay"), 0.75); n += 1
    assert m.blend_value(0.8, 0.5, "add") == 1.0; n += 1
    assert near(m.blend_value(0.2, 0.9, "difference"), 0.7); n += 1
    assert near(m.blend_with_opacity(0.2, 1.0, "normal", 0.5), 0.6); n += 1
    assert m.blend_with_opacity(0.2, 1.0, "normal", 0.0) == 0.2; n += 1
    assert m.blend_with_opacity(0.2, 0.9, "normal", 1.0) == 0.9; n += 1
    assert m.blend_with_opacity(1.0, 1.0, "add", 1.0) == 1.0; n += 1
    assert raises(m.blend_value, 0.1, 0.1, "burn"); n += 1
    assert raises(m.blend_with_opacity, 0.1, 0.1, "normal", 1.5); n += 1
    return n
