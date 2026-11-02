import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_freeze_hold as m


def run():
    n = 0
    assert m.freeze_plan(5, 2, 3) == [0, 1, 2, 2, 2, 2, 3, 4]; n += 1
    assert m.freeze_plan(5, 1, 2, True) == [0, 1, 1, 3, 4]; n += 1
    assert m.freeze_plan(5, 3, 4, True) == [0, 1, 2, 3, 3]; n += 1
    assert m.freeze_plan(5, 99, 2) == [0, 1, 2, 3, 4, 4, 4]; n += 1
    assert m.freeze_plan(5, 99, 2, True) == [0, 1, 2, 3, 4]; n += 1
    assert m.freeze_plan(1, 0, 3) == [0, 0, 0, 0]; n += 1
    assert m.freeze_plan(1, 0, 3, True) == [0]; n += 1
    assert len(m.freeze_plan(10, 0, 1000)) == 1010; n += 1
    assert m.freeze_plan(4, 0, 1) == [0, 0, 1, 2, 3]; n += 1
    for bad, text in (((0, 0, 1), "at least 1 frame"), ((5, 0, 0), "hold_frames must be at least 1")):
        try:
            m.freeze_plan(*bad)
            raise SystemExit("bad args must raise")
        except ValueError as e:
            assert text in str(e)
        n += 1
    assert m.SYFreezeHold.RETURN_TYPES == ("IMAGE", "INT"); n += 1
    return n
