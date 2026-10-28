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
    return n
