import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_picture_in_picture as m


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected ValueError")


def run():
    n = 0
    assert m.inset_box(1000, 600, 400, 200, 0.3, "bottom-right", 24) == (676, 600 - 24 - 150, 300, 150); n += 1
    assert m.inset_box(1000, 600, 400, 200, 0.3, "top-left", 24) == (24, 24, 300, 150); n += 1
    assert m.inset_box(1000, 600, 400, 200, 0.3, "top-right", 10) == (690, 10, 300, 150); n += 1
    assert m.inset_box(1000, 600, 400, 200, 0.3, "bottom-left", 10) == (10, 440, 300, 150); n += 1
    assert m.inset_box(1000, 600, 400, 200, 0.3, "centre", 99) == (350, 225, 300, 150); n += 1
    assert m.inset_box(1000, 600, 100, 100, 0.5, "top-left", 0) == (0, 0, 500, 500); n += 1
    x, y, w, h = m.inset_box(640, 360, 300, 500, 0.2, "bottom-right", 5)
    assert x >= 0 and y >= 0 and x + w <= 640 and y + h <= 360; n += 1
    assert "does not fit" in _raises(m.inset_box, 1000, 600, 100, 100, 0.9, "top-left", 24); n += 1
    assert "does not fit" in _raises(m.inset_box, 100, 100, 100, 200, 0.5, "top-left", 40); n += 1
    assert "position" in _raises(m.inset_box, 100, 100, 10, 10, 0.3, "middle", 0); n += 1
    assert "between 0.05 and 0.9" in _raises(m.inset_box, 100, 100, 10, 10, 0.95, "centre", 0); n += 1
    assert m.round_rect_distance(5, 5, 10, 10, 0) < 0; n += 1
    assert m.round_rect_distance(0.2, 0.2, 10, 10, 4) > 0; n += 1
    assert abs(m.round_rect_distance(5, 0, 10, 10, 4)) < 1e-9; n += 1
    assert m.clip_length(1, 5) == 5 and m.clip_length(8, 3, "stop at shorter") == 3; n += 1
    assert m.clip_length(8, 3, "repeat last") == 8; n += 1
    assert "too thick" in _raises(m.check_border, 40, 60, 60); n += 1
    assert m.check_border(4, 60, 60) is None; n += 1
    assert "when_uneven" in _raises(m.clip_length, 2, 2, "x"); n += 1
    assert m.SYPictureInPicture.RETURN_TYPES == ("IMAGE",); n += 1
    return n
