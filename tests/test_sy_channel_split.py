import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_channel_split as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    assert m.split_pixel((0.1, 0.2, 0.3)) == (0.1, 0.2, 0.3, 1.0); n += 1
    assert m.split_pixel((0.1, 0.2, 0.3, 0.4)) == (0.1, 0.2, 0.3, 0.4); n += 1
    assert m.split_pixel([0, 0, 0]) == (0, 0, 0, 1.0); n += 1
    assert m.split_pixel((1, 0, 0, 0)) == (1, 0, 0, 0); n += 1
    assert m.split_pixel((0.5, 0.5, 0.5))[3] == 1.0; n += 1
    assert len(m.split_pixel((0, 0, 0))) == 4; n += 1
    msg = raises(m.split_pixel, (0.1, 0.2))
    assert msg and "3 or 4" in msg; n += 1
    assert raises(m.split_pixel, ()); n += 1
    assert raises(m.split_pixel, (1, 2, 3, 4, 5)); n += 1
    assert m.SYChannelSplit.RETURN_NAMES == ("red", "green", "blue", "alpha"); n += 1
    assert m.SYChannelSplit.RETURN_TYPES == ("MASK",) * 4; n += 1
    assert "alpha" in m.SYChannelSplit.INPUT_TYPES()["required"]["image"][1]["tooltip"]; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYChannelSplit"] == "Channel Split SY"; n += 1
    assert m.SYChannelSplit.CATEGORY.endswith("Image"); n += 1
    return n
