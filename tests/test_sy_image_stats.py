import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_image_stats as m


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
    mean, std, d, b = m.luma_stats([0.5] * 10, 0.1, 0.9)
    assert near(mean, 0.5) and near(std, 0.0) and d == 0.0 and b == 0.0; n += 1
    mean, std, d, b = m.luma_stats([0.0, 1.0], 0.1, 0.9)
    assert near(mean, 0.5) and near(std, 0.5) and d == 50.0 and b == 50.0; n += 1
    mean, std, d, b = m.luma_stats([0.0, 0.0, 0.0, 1.0], 0.1, 0.9)
    assert near(mean, 0.25) and d == 75.0 and b == 25.0; n += 1
    # strictly below / above: values equal to the level do not count
    _, _, d, b = m.luma_stats([0.1, 0.9], 0.1, 0.9)
    assert d == 0.0 and b == 0.0; n += 1
    mean, std, d, b = m.luma_stats([0.3], 0.1, 0.9)
    assert near(mean, 0.3) and near(std, 0.0); n += 1
    assert near(m.luma_stats([0.2, 0.4, 0.6, 0.8], 0.0, 1.0)[1], (0.05) ** 0.5); n += 1
    _, _, d, b = m.luma_stats([0.0, 0.5, 1.0], 0.0, 1.0)
    assert d == 0.0 and b == 0.0; n += 1
    msg = raises(m.luma_stats, [0.5], 0.9, 0.1)
    assert msg and "dark_level" in msg and "bright_level" in msg; n += 1
    assert raises(m.luma_stats, [0.5], 0.5, 0.5); n += 1
    msg = raises(m.luma_stats, [0.5], -0.1, 0.9)
    assert msg and "dark_level" in msg; n += 1
    msg = raises(m.luma_stats, [0.5], 0.1, 1.5)
    assert msg and "bright_level" in msg; n += 1
    msg = raises(m.luma_stats, [], 0.1, 0.9)
    assert msg and "pixels" in msg; n += 1
    s = m.summary_text(0.5, 0.25, 10.0, 20.0)
    assert "0.500" in s and "0.250" in s and "10.000" in s and "20.000" in s and "\n" not in s; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYImageStats"] == "Image Stats SY"; n += 1
    assert m.SYImageStats.RETURN_NAMES == ("mean", "contrast", "dark_percent", "bright_percent", "summary"); n += 1
    return n
