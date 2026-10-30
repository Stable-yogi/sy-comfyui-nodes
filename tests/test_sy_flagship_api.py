import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import _sy_flagship_api as m
import sy_resolution
import sy_size_presets
import sy_video_size_presets


def raises(fn, *a):
    try:
        fn(*a)
    except (ValueError, TypeError) as e:
        return str(e)
    return None


def run():
    n = 0
    # the live size is the same number the node gives
    q = {"model_preset": "Custom", "aspect": "16:9", "orientation": "landscape", "megapixels": "2.0", "multiple": "16"}
    r = m.size_for("SYResolution", q)
    w, h = sy_resolution.compute_size("Custom", "16:9", "landscape", 2.0, 16)
    assert (r["width"], r["height"]) == (w, h); n += 1
    assert abs(r["megapixels"] - round(w * h / 1e6, 2)) < 1e-9; n += 1
    r = m.size_for("SYSizePresets", {"preset": "1280x720 wide 16:9"})
    assert (r["width"], r["height"]) == (1280, 720); n += 1
    assert m.size_for("SYSizePresets", {"preset": "2048x2048 square"})["megapixels"] == 4.19; n += 1
    r = m.size_for("SYVideoSizePresets", {"resolution": "720p", "aspect": "9:16", "multiple": "16"})
    assert (r["width"], r["height"]) == sy_video_size_presets.video_size("720p", "9:16", 16); n += 1
    assert raises(m.size_for, "SYSeed", {}) and "not a size node" in raises(m.size_for, "SYSeed", {}); n += 1
    assert raises(m.size_for, "SYSizePresets", {"preset": "nope"}); n += 1
    assert raises(m.size_for, "SYResolution", {"megapixels": "abc"}); n += 1
    # the .txt list
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "a", "b", "c", "d"))
        for rel in ("one.txt", "Two.TXT", "pic.png", os.path.join("a", "x.txt"), os.path.join("a", "b", "y.txt"),
                    os.path.join("a", "b", "c", "deep.txt"), os.path.join("a", "b", "c", "d", "deeper.txt")):
            with open(os.path.join(d, rel), "w") as f:
                f.write("t")
        got = m.list_text_files(d)
        assert "one.txt" in got and "Two.TXT" in got and "a/x.txt" in got and "a/b/y.txt" in got; n += 1
        assert "pic.png" not in got; n += 1
        assert "a/b/c/deep.txt" in got; n += 1  # three folders down is still listed
        assert "a/b/c/d/deeper.txt" not in got; n += 1  # four folders down is not
        assert len(m.list_text_files(d, max_files=2)) == 2; n += 1
        assert m.list_text_files(os.path.join(d, "missing")) == []; n += 1
    assert m.register_routes() is False; n += 1  # outside ComfyUI it does nothing
    return n
