import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_reference_picture as m


def must_raise(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected a ValueError")


def run():
    n = 0
    assert m.is_active(True, "a.png") is True; n += 1
    assert m.is_active(False, "a.png") is False and m.is_active(True, "(none)") is False and m.is_active(True, "") is False; n += 1
    assert m.fit_size(2000, 1000, 0) == (2000, 1000); n += 1
    assert m.fit_size(2000, 1000, 1000) == (1000, 500); n += 1
    assert m.fit_size(800, 1600, 800) == (400, 800); n += 1
    assert m.fit_size(500, 400, 1000) == (500, 400); n += 1  # never scales up
    assert m.fit_size(10000, 1, 100) == (100, 1); n += 1  # never below 1 pixel
    assert "size" in must_raise(m.fit_size, 0, 5, 10); n += 1
    assert m.make_label(1, "the hero", True) == "Image 1: the hero"; n += 1
    assert m.make_label(2, "  two   words ", True) == "Image 2: two words"; n += 1
    assert m.make_label(3, "", True) == "Image 3" and m.make_label(3, "x", False) == ""; n += 1
    assert "slot" in must_raise(m.make_label, 0, "x", True); n += 1
    assert m.SYReferencePicture.RETURN_NAMES == ("image", "mask", "width", "height", "active", "label"); n += 1
    spec = m.SYReferencePicture.INPUT_TYPES()
    assert spec["required"]["image"][0][-1] == "(none)" and spec["required"]["image"][1]["image_upload"] is True; n += 1
    return n
