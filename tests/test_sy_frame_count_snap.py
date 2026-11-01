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
    assert m.SYFrameCountSnap().run(80, 4, "nearest", True)[:2] == (81, f(80, 4, "nearest", True)[1]); n += 1
    assert m.SYFrameCountSnap.RETURN_TYPES[:2] == ("INT", "STRING"); n += 1
    return n + _extra(m)


def _extra(m):
    n = 0
    def ok(c):
        assert c
        return 1
    def rs(fn, *a, **k):
        try:
            fn(*a, **k)
        except ValueError as e:
            return str(e)
        return None
    n += ok(m.snap_frames(200, 4, 'nearest', True, 121)[0] == 121)
    n += ok('capped by max_frames 121' in m.snap_frames(200, 4, 'nearest', True, 121)[1])
    n += ok(m.snap_frames(80, 4, 'nearest', True, 0) == m.snap_frames(80, 4, 'nearest', True))
    n += ok(m.snap_frames(80, 4, 'nearest', True, 500)[0] == 81)
    n += ok(m.snap_frames(100, 8, 'up', False, 50)[0] == 48)
    n += ok('too small' in rs(m.snap_frames, 80, 8, 'nearest', True, 5))
    n += ok(m.SYFrameCountSnap().run(80, 4, 'nearest', True, 0, 24.0)[2] == 81 / 24.0)
    n += ok(rs(m.SYFrameCountSnap().run, 80, 4, 'nearest', True, 0, 0.0) is not None)
    return n
