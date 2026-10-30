import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_duotone as m
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
    assert hx.parse_hex("#ff0000") == (1.0, 0.0, 0.0); n += 1
    assert hx.parse_hex("0F0") == (0.0, 1.0, 0.0); n += 1
    assert near(hx.parse_hex("#D4A537")[0], 0xD4 / 255.0); n += 1
    assert hx.parse_hex("  #abc ") == hx.parse_hex("aabbcc"); n += 1
    msg = raises(hx.parse_hex, "#12345", "shadow_colour")
    assert msg and "shadow_colour" in msg; n += 1
    assert raises(hx.parse_hex, "zzzzzz", "x"); n += 1
    assert raises(hx.parse_hex, "", "x"); n += 1
    assert raises(hx.parse_hex, 5, "x"); n += 1
    assert hx.to_hex((1.0, 0.0, 0.5)) == "#ff0080"; n += 1
    s, h = (0.1, 0.2, 0.3), (0.9, 0.8, 0.7)
    assert m.map_luma(0.0, s, h) == s; n += 1
    assert all(near(a, b) for a, b in zip(m.map_luma(1.0, s, h), h)); n += 1
    assert all(near(a, 0.5) for a in m.map_luma(0.5, s, h)); n += 1
    assert m.map_luma(-3.0, s, h) == s; n += 1
    assert all(near(a, b) for a, b in zip(m.map_luma(7.0, s, h), h)); n += 1
    # pixel: black goes to shadow, white to highlight, strength 0 keeps the original
    assert all(near(a, b) for a, b in zip(m.duotone_pixel((0, 0, 0), s, h, 1.0), s)); n += 1
    assert all(near(a, b) for a, b in zip(m.duotone_pixel((1, 1, 1), s, h, 1.0), h)); n += 1
    assert m.duotone_pixel((0.2, 0.4, 0.6), s, h, 0.0) == (0.2, 0.4, 0.6); n += 1
    half = m.duotone_pixel((0, 0, 0), s, h, 0.5)
    assert near(half[0], 0.05) and near(half[2], 0.15); n += 1
    assert raises(m.duotone_pixel, (0, 0, 0), s, h, 1.5); n += 1
    assert near(m.luma709(1, 1, 1), 1.0); n += 1
    assert m.DEFAULT_SHADOW == "#1b1b2f" and m.DEFAULT_HIGHLIGHT == "#f5d58a"; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYDuotone"] == "Duotone SY"; n += 1
    return n
