import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_duration_frames as m


def raises(*args):
    try:
        m.convert(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    c = m.convert
    assert c("seconds_to_frames", 5.0, 0, 24.0)[0] == 120; n += 1
    assert c("seconds_to_frames", 5.0, 0, 24.0)[1] == 5.0; n += 1
    assert c("seconds_to_frames", 1.0, 0, 29.97)[0] == 30; n += 1
    assert c("seconds_to_frames", 0.0, 0, 24.0)[0] == 0; n += 1
    assert c("seconds_to_frames", 2.5, 0, 25.0)[0] == 63; n += 1
    assert c("frames_to_seconds", 0.0, 48, 24.0)[1] == 2.0; n += 1
    assert c("frames_to_seconds", 0.0, 48, 24.0)[0] == 48; n += 1
    assert abs(c("frames_to_seconds", 0.0, 100, 30.0)[1] - 3.3333333) < 1e-5; n += 1
    assert "frames" in c("frames_to_seconds", 0.0, 10, 10.0)[2]; n += 1
    assert raises("seconds_to_frames", 1.0, 0, 0); n += 1
    assert raises("seconds_to_frames", 1.0, 0, -24.0); n += 1
    assert raises("seconds_to_frames", -1.0, 0, 24.0); n += 1
    assert raises("frames_to_seconds", 0.0, -1, 24.0); n += 1
    assert raises("backwards", 1.0, 1, 24.0); n += 1
    assert m.SYDurationFrames().run("seconds_to_frames", 5.0, 0, 24.0)[0] == 120; n += 1
    assert m.SYDurationFrames.RETURN_TYPES == ("INT", "FLOAT", "STRING"); n += 1
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
    n += ok(m.convert('seconds_to_frames', 5.0, 0, 24.0)[0] == 120)
    n += ok(m.convert('seconds_to_frames', 5.0, 0, 24.0, '4n+1')[0] == 121)
    n += ok('snapped from 120' in m.convert('seconds_to_frames', 5.0, 0, 24.0, '4n+1')[2])
    n += ok(abs(m.convert('seconds_to_frames', 5.0, 0, 24.0, '4n+1')[1] - 121 / 24.0) < 1e-9)
    n += ok(m.convert('seconds_to_frames', 0.0, 0, 24.0, '8n+1')[0] == 9)
    n += ok('does not fit the 4n+1' in m.convert('frames_to_seconds', 0, 120, 24.0, '4n+1')[2])
    n += ok('note' not in m.convert('frames_to_seconds', 0, 121, 24.0, '4n+1')[2])
    n += ok(rs(m.convert, 'frames_to_seconds', 0, 10, 24.0, 'bogus') is not None)
    n += ok(m.convert('seconds_to_frames', 5.0, 0, 24.0, 'none') == m.convert('seconds_to_frames', 5.0, 0, 24.0))
    return n
