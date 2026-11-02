import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_letterbox as m


def bad(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert abs(m.parse_aspect("2.39:1") - 2.39) < 1e-9; n += 1
    assert abs(m.parse_aspect("16:9") - 16 / 9.0) < 1e-9; n += 1
    assert abs(m.parse_aspect("2.35") - 2.35) < 1e-9; n += 1
    assert abs(m.parse_aspect(" 1:1 ") - 1.0) < 1e-9; n += 1
    for t in ("", "abc", "16:0", "-2", "1:2:3", None, "999"):
        assert bad(m.parse_aspect, t), t; n += 1
    # narrower than aspect: side bars, canvas grows
    ow, oh, l, t, box = m.plan_letterbox(1920, 1080, "2.39:1", "add bars")
    assert (ow, oh, t, box) == (2581, 1080, 0, (0, 0, 1920, 1080)) and l == (2581 - 1920) // 2; n += 1
    # wider than aspect: bars top and bottom
    ow, oh, l, t, box = m.plan_letterbox(1920, 800, "16:9", "add bars")
    assert (ow, oh, l) == (1920, 1080, 0) and t == 140; n += 1
    # already right
    assert m.plan_letterbox(1600, 900, "16:9", "add bars")[:4] == (1600, 900, 0, 0); n += 1
    # crop
    ow, oh, l, t, box = m.plan_letterbox(1920, 1080, "2.39:1", "crop to fit")
    assert ow == 1920 and oh == 803 and box == (0, 138, 1920, 941); n += 1
    ow, oh, l, t, box = m.plan_letterbox(1920, 1080, "1:1", "crop to fit")
    assert (ow, oh, box) == (1080, 1080, (420, 0, 1500, 1080)); n += 1
    assert bad(m.plan_letterbox, 100, 100, "2:1", "squash"); n += 1
    assert bad(m.plan_letterbox, 0, 100, "2:1", "add bars"); n += 1
    assert bad(m.plan_letterbox, 100, 100, "nope", "add bars"); n += 1
    s = m.letterbox_info(1920, 800, 1920, 1080, 0, 140, "add bars")
    assert s == "1920x800 -> 1920x1080 with 2 bars of 140 px", s; n += 1
    assert "no bars" in m.letterbox_info(1600, 900, 1600, 900, 0, 0, "add bars"); n += 1
    assert "cropped" in m.letterbox_info(1920, 1080, 1920, 803, 0, 0, "crop to fit"); n += 1
    assert "already" in m.letterbox_info(10, 10, 10, 10, 0, 0, "crop to fit"); n += 1
    assert m.SYLetterbox.RETURN_NAMES == ("image", "info"); n += 1
    return n  # checks
