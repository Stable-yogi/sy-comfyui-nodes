import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_luminance_mask as m


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
    assert m.band_value(0.5, 0.2, 0.8, 0.0) == 1.0; n += 1
    assert m.band_value(0.2, 0.2, 0.8, 0.0) == 1.0 and m.band_value(0.8, 0.2, 0.8, 0.0) == 1.0; n += 1
    assert m.band_value(0.1, 0.2, 0.8, 0.0) == 0.0 and m.band_value(0.9, 0.2, 0.8, 0.0) == 0.0; n += 1
    assert m.band_value(0.0, 0.0, 1.0, 0.0) == 1.0 and m.band_value(1.0, 0.0, 1.0, 0.0) == 1.0; n += 1
    assert near(m.band_value(0.15, 0.2, 0.8, 0.1), 0.5); n += 1
    assert near(m.band_value(0.85, 0.2, 0.8, 0.1), 0.5); n += 1
    assert m.band_value(0.05, 0.2, 0.8, 0.1) == 0.0; n += 1
    assert m.band_value(0.95, 0.2, 0.8, 0.1) == 0.0; n += 1
    assert near(m.band_value(0.19, 0.2, 0.8, 0.5), 0.98); n += 1
    assert m.band_value(0.5, 0.5, 0.5, 0.0) == 1.0; n += 1  # low equals high is a single level
    assert m.band_value(0.51, 0.5, 0.5, 0.0) == 0.0; n += 1
    # symmetric fade
    assert near(m.band_value(0.3 - 0.04, 0.3, 0.6, 0.2), m.band_value(0.6 + 0.04, 0.3, 0.6, 0.2)); n += 1
    msg = raises(m.band_value, 0.5, 0.9, 0.1, 0.0)
    assert msg and "low must not be above high" in msg; n += 1
    assert raises(m.band_value, 0.5, 0.0, 1.0, 0.6); n += 1
    assert raises(m.band_value, 0.5, 0.0, 1.0, -0.1); n += 1
    assert raises(m.band_value, 0.5, -0.1, 1.0, 0.0); n += 1
    assert raises(m.band_value, 0.5, 0.0, 1.5, 0.0); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYLuminanceMask"] == "Luminance Mask SY"; n += 1
    assert m.SYLuminanceMask.RETURN_TYPES == ("MASK", "STRING"); n += 1
    assert m.check_source("red") is None and raises(m.check_source, "alpha"); n += 1
    t = m.mask_info("luminance", 0.5, 1.0, 0.1, True, 4, 35.0)
    assert "brightness between 0.5 and 1" in t and "soft fade of 0.1" in t and "inverted" in t and "feathered 4 px" in t and "35.0% selected" in t; n += 1
    assert "the red channel" in m.mask_info("red", 0.0, 1.0, 0.0, False, 0, 50.0) and "soft fade" not in m.mask_info("red", 0.0, 1.0, 0.0, False, 0, 50.0); n += 1
    assert "empty" in m.mask_info("luminance", 0.9, 1.0, 0.0, False, 0, 0.0) and "Widen" in m.mask_info("luminance", 0.9, 1.0, 0.0, False, 0, 0.0); n += 1
    assert "whole picture" in m.mask_info("luminance", 0.0, 1.0, 0.0, False, 0, 100.0); n += 1
    assert m.SYLuminanceMask.RETURN_NAMES == ("mask", "info"); n += 1
    assert list(m.SYLuminanceMask.INPUT_TYPES()["optional"]) == ["source", "feather"]; n += 1
    return n
