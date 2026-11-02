import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_duplicate_frame_drop as m


def run():
    n = 0
    assert m.pick_kept([0, 0.5, 0.0, 0.0, 0.3], 0.004) == [0, 1, 4]
    assert m.pick_kept([0, 0.004, 0.005], 0.004) == [0, 2]            # equal to tolerance counts as a copy
    assert m.pick_kept([0, 0.0, 0.0], 0.004) == [0]
    assert m.pick_kept([0, 0.0, 0.5], 0.004, False) == [2]
    n += 4
    # edge: one frame, all frames copies with keep_first off, zero tolerance
    assert m.pick_kept([0.0], 0.0) == [0]
    assert m.pick_kept([0.0], 0.0, False) == [0]
    assert m.pick_kept([0, 0.0, 0.0], 0.0, False) == [0]
    assert m.pick_kept([0, 0.001], 0.0) == [0, 1]
    n += 4
    assert m.format_indices([0, 1, 4]) == "0,1,4"
    assert m.format_indices([0]) == "0"
    n += 2
    for call in (lambda: m.pick_kept([], 0.004), lambda: m.pick_kept([0, 1], 0.5), lambda: m.pick_kept([0, 1], -0.1)):
        try:
            call()
            raise SystemExit("bad args must raise")
        except ValueError as e:
            assert str(e)
        n += 1
    assert m.SYDuplicateFrameDrop.RETURN_TYPES == ("IMAGE", "STRING", "INT")
    n += 1
    return n
