import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_video_frame_counter as m

N = [0]


def ok(cond, msg="check failed"):
    N[0] += 1
    if not cond:
        raise AssertionError(msg)


def raises(fn, *args):
    N[0] += 1
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError("expected ValueError for %r" % (args,))


def run():
    f, s, r, info = m.count_video("frames_to_seconds", 81, 0, 16)
    ok(f == 81 and abs(s - 5.0625) < 1e-9 and r == 16.0)
    ok(info == "81 frames, 5.062 seconds, 16.000 fps" or info.startswith("81 frames, 5.06"))
    f, s, r, _ = m.count_video("seconds_to_frames", 0, 5, 16)
    ok(f == 80 and s == 5.0 and r == 16.0)
    f, s, r, _ = m.count_video("fps_from_frames_and_seconds", 120, 5, 0)
    ok(f == 120 and s == 5.0 and abs(r - 24.0) < 1e-9)
    ok(m.count_video("seconds_to_frames", 0, 0.01, 1)[0] == 1)
    raises(m.count_video, "bad_mode", 1, 1, 1)
    raises(m.count_video, "frames_to_seconds", 0, 1, 16)
    raises(m.count_video, "frames_to_seconds", 10, 1, 0)
    raises(m.count_video, "seconds_to_frames", 1, float("nan"), 16)
    raises(m.count_video, "seconds_to_frames", 1, 100000, 1000)
    raises(m.count_video, "fps_from_frames_and_seconds", 10, 0, 1)
    ok(m.SYVideoFrameCounter().run("frames_to_seconds", 24, 1, 24)[0] == 24)
    return N[0]
