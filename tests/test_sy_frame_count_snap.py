import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_frame_count_snap as m


def raises(*args):
    try:
        m.snap_frames(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    f = m.snap_frames
    assert f(80, 4, "nearest", True)[0] == 81; n += 1
    assert f(80, 4, "nearest", False)[0] == 80; n += 1
    assert f(81, 4, "down", False)[0] == 80; n += 1
    assert f(81, 4, "up", False)[0] == 84; n += 1
    assert f(82, 4, "nearest", False)[0] == 84; n += 1  # half rounds up
    assert f(81, 4, "nearest", False)[0] == 80; n += 1
    assert f(1, 4, "down", False)[0] == 4; n += 1  # never below one step
    assert f(1, 8, "nearest", True)[0] == 9; n += 1
    assert f(7, 1, "nearest", False)[0] == 7; n += 1
    assert f(100, 8, "up", True)[0] == 105; n += 1
    assert isinstance(f(80, 4, "nearest", True)[1], str) and "81" in f(80, 4, "nearest", True)[1]; n += 1
    assert raises(0, 4, "nearest", True); n += 1
    assert raises(80, 0, "nearest", True); n += 1
    assert raises(80, 4, "sideways", True); n += 1
    assert raises(-5, 4, "nearest", True); n += 1
    assert m.SYFrameCountSnap().run(80, 4, "nearest", True) == (81, f(80, 4, "nearest", True)[1]); n += 1
    assert m.SYFrameCountSnap.RETURN_TYPES == ("INT", "STRING"); n += 1
    return n
