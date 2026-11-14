import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_video_frame_picker as m
import _sy_video_info_api as api


def refuses(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return ""


def run():
    n = 0
    assert m.pick_videos(["b.mp4", "a.MOV", "x.png", "c.webm"]) == ["(none)", "a.MOV", "b.mp4", "c.webm"]; n += 1
    assert m.clamp_frame(5, 100) == (5, ""); n += 1
    idx, note = m.clamp_frame(150, 100)
    assert idx == 99 and "past the end" in note; n += 1
    assert m.clamp_frame(7, 0) == (7, ""); n += 1   # unknown length: kept
    assert "negative" in refuses(m.clamp_frame, -1, 10); n += 1
    assert m.frame_of_time(0, 24) == 0 and m.frame_of_time(1.0, 24) == 24 and m.frame_of_time(41 / 24, 24) == 41; n += 1
    assert m.frame_of_time(10 / 29.97, 29.97) == 10; n += 1
    assert "frame rate" in refuses(m.frame_of_time, 1.0, 0); n += 1
    t = m.info_text("clip.mp4", 48, 120, 24.0, 640, 360)
    assert "frame 48 (last frame 119), 2.000 s" in t and "640x360" in t; n += 1
    assert api.check_video_name("sub/clip.mp4") == "sub/clip.mp4" and api.check_video_name("a.webm [input]"); n += 1
    for bad in ("../x.mp4", "C:/x.mp4", "/etc/x.mp4", "a.png", "", "a\x00.mp4"):
        assert refuses(api.check_video_name, bad), bad
    n += 1
    here = os.path.dirname(os.path.abspath(__file__))
    assert api.inside(os.path.join(here, "x.mp4"), here) and not api.inside(os.path.join(here, "..", "x.mp4"), here); n += 1
    it = m.SYVideoFramePicker.INPUT_TYPES()["required"]
    assert list(it) == ["video", "frame"] and it["video"][1].get("video_upload") is True; n += 1
    assert m.SYVideoFramePicker.RETURN_NAMES == ("image", "frame", "seconds", "info"); n += 1
    assert "pick a video" in refuses(m.SYVideoFramePicker().run, "(none)", 0); n += 1
    assert "SYVideoFramePicker" in m.NODE_CLASS_MAPPINGS and m.NODE_DISPLAY_NAME_MAPPINGS["SYVideoFramePicker"] == "Video Frame Picker SY"; n += 1
    return n


if __name__ == "__main__":
    print("checks:", run())
