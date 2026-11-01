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
    # --- value pass A2: 4n+1 rule note and nearest valid count
    import _sy_a2_video as v
    ok(v.snap_frames(81) == 81 and v.snap_frames(80) == 81 and v.snap_frames(82) == 81 and v.snap_frames(83) == 85)
    ok(v.snap_frames(80, 4, "down") == 77 and v.snap_frames(82, 4, "up") == 85 and v.snap_frames(81, 4, "up") == 81)
    ok(v.snap_frames(0) == 1 and v.snap_frames(2) == 1 and v.snap_frames(3) == 5)
    ok(v.snap_frames(100, 8) == 97 and v.snap_frames(101, 8, "up") == 105 and v.snap_frames(10, 1) == 10)
    raises(v.snap_frames, 5, 0)
    raises(v.snap_frames, 5, 4, "sideways")
    ok(v.is_valid_count(81) and not v.is_valid_count(80) and v.is_valid_count(97, 8))
    ok(v.rule_note(81) == "81 frames fits the 4n+1 rule.")
    ok(v.rule_note(80) == "80 frames does not fit the 4n+1 rule. Use 77 (shorter) or 81 (longer).")
    ok(v.rule_note(100, 8) == "100 frames does not fit the 8n+1 rule. Use 97 (shorter) or 105 (longer).")
    out = m.SYVideoFrameCounter().run("frames_to_seconds", 80, 1, 16)
    ok(len(out) == len(m.SYVideoFrameCounter.RETURN_TYPES) == len(m.SYVideoFrameCounter.RETURN_NAMES) == 6 and out[4] == 81 and "Use 77" in out[5])
    out = m.SYVideoFrameCounter().run("seconds_to_frames", 1, 5, 16, 8)
    ok(out[0] == 80 and out[4] == 81 and "8n+1" in out[5])
    return N[0]
