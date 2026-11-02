import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_split_screen as m


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected ValueError")


def run():
    n = 0
    assert m.split_masks_plan("side by side", 0.5, 10, 3) == [5, 5, 5]; n += 1
    assert m.split_masks_plan("side by side", 0.25, 100, 2) == [25, 25]; n += 1
    assert m.split_masks_plan("stacked", 0.5, 8, 4) == [8, 8, 0, 0]; n += 1
    assert m.split_masks_plan("diagonal split", 0.5, 10, 5) == [10, 8, 5, 2, 0]; n += 1
    assert m.split_regions("side by side", 0.5, 20, 2, 4)[0] == (8, 12); n += 1
    assert m.split_regions("stacked", 0.5, 8, 10, 2)[3:7] == [(8, 8), (0, 8), (0, 8), (0, 0)]; n += 1
    assert m.split_regions("side by side", 0.05, 100, 2, 10)[0] == (0, 10); n += 1
    assert m.split_regions("side by side", 0.95, 100, 2, 10)[0] == (90, 100); n += 1
    assert m.fill_crop_box(200, 100, 100, 100) == (50, 0, 100, 100); n += 1
    assert m.fill_crop_box(100, 200, 100, 100) == (0, 50, 100, 100); n += 1
    assert m.fill_crop_box(64, 64, 32, 32) == (0, 0, 64, 64); n += 1
    assert m.clip_length(10, 4, "stop at shorter") == 4; n += 1
    assert m.clip_length(10, 4, "repeat last") == 10; n += 1
    assert m.clip_length(1, 7, "stop at shorter") == 7; n += 1
    assert m.clip_length(5, 1) == 5; n += 1
    assert "layout" in _raises(m.split_regions, "circle", 0.5, 10, 10, 0); n += 1
    assert "between 0.05 and 0.95" in _raises(m.split_regions, "stacked", 0.99, 10, 10, 0); n += 1
    assert "Lower it" in _raises(m.split_regions, "side by side", 0.5, 10, 10, 10); n += 1
    assert "too small" in _raises(m.split_regions, "side by side", 0.5, 1, 10, 0); n += 1
    assert "at least one picture" in _raises(m.clip_length, 0, 3); n += 1
    assert "when_uneven" in _raises(m.clip_length, 2, 3, "cut"); n += 1
    assert m.SYSplitScreen.RETURN_TYPES == ("IMAGE",); n += 1
    return n
