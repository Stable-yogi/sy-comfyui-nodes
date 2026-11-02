import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_sharpest_frame_pick as m


def _raises(call, text):
    try:
        call()
    except ValueError as e:
        assert text in str(e), str(e)
        return 1
    raise SystemExit("expected ValueError: " + text)


def run():
    n = 0
    flat = [[0.5] * 5 for _ in range(5)]
    assert m.sharpness_score(flat) == 0.0; n += 1
    ramp = [[x * 0.1 for x in range(5)] for _ in range(5)]       # straight slope: second difference is 0
    assert abs(m.sharpness_score(ramp)) < 1e-12; n += 1
    checker = [[(x + y) % 2 * 1.0 for x in range(5)] for y in range(5)]
    sharp = m.sharpness_score(checker)
    soft = m.sharpness_score([[0.5 + 0.1 * ((x + y) % 2) for x in range(5)] for y in range(5)])
    assert sharp > soft > 0.0; n += 1
    dot = [[0.0] * 3 for _ in range(3)]
    dot[1][1] = 1.0
    assert m.sharpness_score(dot) == 0.0; n += 1                  # a single inside value has no spread
    big = [[0.0] * 4 for _ in range(4)]
    big[1][1] = 1.0
    assert m.sharpness_score(big) > 0.0; n += 1
    assert m.pick_sharpest([1.0, 5.0, 3.0], 1) == [1]; n += 1
    assert m.pick_sharpest([1.0, 5.0, 3.0], 2) == [1, 2]; n += 1
    assert m.pick_sharpest([1.0, 5.0, 3.0], 2, "best first") == [1, 2]; n += 1
    assert m.pick_sharpest([5.0, 1.0, 3.0], 3, "best first") == [0, 2, 1]; n += 1
    assert m.pick_sharpest([5.0, 1.0, 3.0], 3) == [0, 1, 2]; n += 1
    assert m.pick_sharpest([2.0, 2.0, 2.0], 2) == [0, 1]; n += 1       # ties go to the earlier frame
    assert m.pick_sharpest([1.0, 2.0], 64) == [0, 1]; n += 1
    n += _raises(lambda: m.sharpness_score([[0.1, 0.2], [0.3, 0.4]]), "at least 3 x 3")
    n += _raises(lambda: m.sharpness_score([]), "empty")
    n += _raises(lambda: m.sharpness_score([[0, 0, 0], [0, 0], [0, 0, 0]]), "different lengths")
    n += _raises(lambda: m.pick_sharpest([], 1), "empty")
    n += _raises(lambda: m.pick_sharpest([1.0], 0), "keep must be at least 1")
    n += _raises(lambda: m.pick_sharpest([1.0], 1, "worst"), "keep_order must be one of")
    assert m.SYSharpestFramePick.RETURN_TYPES == ("IMAGE", "STRING"); n += 1
    return n
