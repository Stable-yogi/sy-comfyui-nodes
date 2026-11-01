import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_load_clip as m


def must_raise(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected a ValueError")


def run():
    n = 0
    assert m.pick_files(["b.MP4", "a.mov", "x.png", "c.txt"], m.VIDEO_EXT) == ["(none)", "a.mov", "b.MP4"]; n += 1
    assert m.pick_files([], m.AUDIO_EXT) == ["(none)"]; n += 1
    assert m.plan_trim(240, 24, 0, 0, 0) == (0, 240); n += 1
    assert m.plan_trim(240, 24, 2, 3, 0) == (48, 72); n += 1
    assert m.plan_trim(240, 24, 9, 5, 0) == (216, 24); n += 1  # asks for more than is left: stops at the end
    assert m.plan_trim(240, 24, 0, 0, 100) == (0, 100); n += 1
    assert m.plan_trim(240, 24, 1, 0.01, 0) == (24, 1); n += 1  # never fewer than one frame
    assert "after the end" in must_raise(m.plan_trim, 240, 24, 10, 0, 0); n += 1
    assert "frame rate" in must_raise(m.plan_trim, 240, 0, 0, 0, 0); n += 1
    assert "negative" in must_raise(m.plan_trim, 240, 24, -1, 0, 0); n += 1
    assert m.audio_range(480000, 48000, 24, 48, 24) == (48000, 144000); n += 1
    assert m.audio_range(100000, 48000, 24, 48, 24) == (48000, 100000); n += 1  # sound shorter than the video
    assert m.audio_trim_range(96000, 48000, 0, 0) == (0, 96000); n += 1
    assert m.audio_trim_range(96000, 48000, 0.5, 1) == (24000, 72000); n += 1
    assert "after the end" in must_raise(m.audio_trim_range, 96000, 48000, 5, 0); n += 1
    t = m.info_text("video", 72, 24.0, 3.0, 832, 480, True)
    assert t == "Video: 72 frame(s) at 24.000 fps = 3.00 s, 832x480 (trimmed)"; n += 1
    assert m.info_text("sound", 0, 0, 2.5) == "Sound: 2.50 s"; n += 1
    assert m.SYLoadClip.RETURN_NAMES == ("images", "audio", "fps", "frame_count", "seconds", "info"); n += 1
    return n
