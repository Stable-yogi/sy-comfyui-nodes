import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_video_file_upscale as m


def _raises(fn, *args, text=""):
    try:
        fn(*args)
    except ValueError as e:
        assert text in str(e), str(e)
        return
    raise SystemExit("expected ValueError")


def run():
    n = 0
    assert m.final_size(1280, 720, 1920) == (1920, 1080); n += 1
    assert m.final_size(720, 1280, 1920) == (1080, 1920); n += 1
    assert m.final_size(641, 481, 1000) == (1000, 750); n += 1
    for w, h, l in ((333, 777, 1920), (1920, 1080, 256), (101, 99, 4096)):
        fw, fh = m.final_size(w, h, l)
        assert fw % 2 == 0 and fh % 2 == 0 and abs(max(fw, fh) - l) <= 1; n += 1
    _raises(m.final_size, 0, 10, 1920, text="at least 1x1"); n += 1
    assert m.chunk_ranges(10, 4) == [(0, 4), (4, 8), (8, 10)]; n += 1
    assert m.chunk_ranges(3, 16) == [(0, 3)]; n += 1
    assert len(m.chunk_ranges(2160, 16)) == 135; n += 1
    _raises(m.chunk_ranges, 0, 4, text="no frames"); n += 1
    _raises(m.chunk_ranges, 5, 0, text="at least 1"); n += 1
    assert m.blend_weights(1.0) == (1.0, 0.0); n += 1
    assert m.blend_weights(0.25) == (0.25, 0.75); n += 1
    _raises(m.blend_weights, 1.5, text="between 0 and 1"); n += 1
    _raises(m.blend_weights, float("nan"), text="between 0 and 1"); n += 1
    assert m.blend_values([1.0, 0.0], [0.0, 1.0], 0.5) == [0.5, 0.5]; n += 1
    assert m.blend_values([1.0], [0.0], 1.0) == [1.0] and m.blend_values([1.0], [0.0], 0.0) == [0.0]; n += 1
    assert m.output_name("SY/upscaled", 5) == "SY/upscaled_00005.mp4"; n += 1
    assert m.output_name("clip\\sub", 12) == "clip/sub_00012.mp4"; n += 1
    for bad in ("", "../x", "a/../b", "C:/x", "/abs"):
        _raises(m.output_name, bad, 1, text="filename_prefix"); n += 1
    assert m.check_video_name("a.mp4") == "a.mp4"; n += 1
    assert m.check_video_name("sub\\a.mp4") == "sub/a.mp4"; n += 1
    for bad in ("", "  ", "../a.mp4", "a/../../b.mp4", "C:\\v.mp4", "/etc/v.mp4"):
        _raises(m.check_video_name, bad, text="video"); n += 1
    assert "135 chunks" in m.info_text((1280, 720), (1920, 1080), 2160, 135, 0.65, True); n += 1
    assert "no sound" in m.info_text((2, 2), (4, 4), 1, 1, 1.0, False); n += 1
    spec = m.SYVideoFileUpscale.INPUT_TYPES()["required"]
    assert list(spec) == ["video", "upscale_model", "longest_side", "detail_strength", "chunk_frames", "filename_prefix"]; n += 1
    assert m.SYVideoFileUpscale.RETURN_NAMES == ("video_path", "info"); n += 1
    return n
