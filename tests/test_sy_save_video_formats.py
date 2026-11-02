import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_save_video_formats as m


def _raises(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.safe_prefix("sy_video") == "sy_video" and m.safe_prefix("clip-1.final") == "clip-1.final"
    n += 2
    for bad in ("", "  ", "a/b", "a\\b", "..", "a..b", "../x", "C:x", "a*b", "con", " x", "x.", "x" * 101):
        assert _raises(m.safe_prefix, bad), bad
    n += 13
    assert m.next_free_name([], "v", ".mp4") == "v_00001.mp4"
    assert m.next_free_name(["v_00001.mp4", "v_00007.mp4", "v_00003.webm", "w_00009.mp4"], "v", ".mp4") == "v_00008.mp4"
    assert m.next_free_name(["V_00002.MP4"], "v", ".mp4") == "v_00003.mp4"
    assert m.next_free_name(["v_x_00005.mp4"], "v", ".mp4") == "v_00001.mp4"
    assert _raises(m.next_free_name, [], "a/b", ".mp4") and _raises(m.next_free_name, [], "v", "mp4")
    n += 5
    assert m.quality_to_settings("mp4_h264", "high")["crf"] < m.quality_to_settings("mp4_h264", "low")["crf"]
    assert m.quality_to_settings("webm_vp9", "medium")["codec"] == "libvpx-vp9"
    assert [m.quality_to_settings("gif", q)["colors"] for q in m.QUALITIES] == [64, 128, 256]
    assert m.quality_to_settings("webp_animated", "low")["quality"] < m.quality_to_settings("webp_animated", "high")["quality"]
    assert _raises(m.quality_to_settings, "avi", "low") and _raises(m.quality_to_settings, "gif", "ultra")
    for f in m.FORMATS:
        for q in m.QUALITIES:
            assert m.quality_to_settings(f, q)
    n += 5 + 12
    assert m.even_size(640, 480) == (640, 480) and m.even_size(641, 481) == (640, 480) and m.even_size(3, 2) == (2, 2)
    assert _raises(m.even_size, 1, 10)
    n += 2
    assert m.frame_duration_ms(24) == 42 and m.frame_duration_ms(1000) == 1 and _raises(m.frame_duration_ms, 0)
    n += 1
    assert m.SYSaveVideoFormats.OUTPUT_NODE and m.SYSaveVideoFormats.RETURN_TYPES == ("STRING",)
    assert list(m.SYSaveVideoFormats.INPUT_TYPES()["optional"]) == ["audio"]
    n += 2
    try:
        import torch
        import tempfile
        frames = torch.rand(4, 17, 25, 3)
        with tempfile.TemporaryDirectory() as tmp:
            for fmt in ("gif", "webp_animated"):
                p = m.save_video(frames, tmp, "t" + m.EXTENSIONS[fmt], fmt, "low", 12)
                assert os.path.getsize(p) > 0
                n += 1
            assert _raises(m.save_video, frames, tmp, "t.gif", "gif", "low", 12)   # never overwrites
            n += 1
    except ImportError:
        pass
    return n
