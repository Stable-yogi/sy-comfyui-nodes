import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_batch_average as m


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected ValueError")


def run():
    n = 0
    assert m.frame_weights(4) == [0.25, 0.25, 0.25, 0.25]; n += 1
    assert abs(sum(m.frame_weights(7, "fade in")) - 1.0) < 1e-12; n += 1
    assert m.frame_weights(3, "fade in") == [1 / 6, 2 / 6, 3 / 6]; n += 1
    assert m.frame_weights(3, "fade out") == [3 / 6, 2 / 6, 1 / 6]; n += 1
    assert m.frame_weights(1, "fade out") == [1.0]; n += 1
    assert m.used_range(10, 0, 0) == (0, 10); n += 1
    assert m.used_range(10, 3, 4) == (3, 7); n += 1
    assert m.used_range(10, 8, 50) == (8, 10); n += 1
    assert "at least one frame" in _raises(m.frame_weights, 0); n += 1
    assert "weighting" in _raises(m.frame_weights, 3, "bounce"); n += 1
    assert "Lower start" in _raises(m.used_range, 5, 5, 0); n += 1
    assert "no pictures" in _raises(m.used_range, 0, 0, 0); n += 1
    assert m.SYBatchAverage.RETURN_TYPES == ("IMAGE",); n += 1
    return n
