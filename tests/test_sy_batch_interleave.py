import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_batch_interleave as m


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected ValueError")


def run():
    n = 0
    assert m.interleave_plan(2, 2) == [("a", 0), ("b", 0), ("a", 1), ("b", 1)]; n += 1
    assert m.interleave_plan(3, 1, "keep the rest") == [("a", 0), ("b", 0), ("a", 1), ("a", 2)]; n += 1
    assert m.interleave_plan(1, 3, "keep the rest") == [("a", 0), ("b", 0), ("b", 1), ("b", 2)]; n += 1
    assert m.interleave_plan(3, 1, "stop at shorter") == [("a", 0), ("b", 0)]; n += 1
    assert m.interleave_plan(1, 3, "stop at shorter") == [("a", 0), ("b", 0)]; n += 1
    assert m.interleave_plan(1, 1) == [("a", 0), ("b", 0)]; n += 1
    assert len(m.interleave_plan(100, 37)) == 137; n += 1
    assert len(m.interleave_plan(100, 37, "stop at shorter")) == 74; n += 1
    assert "at least one picture" in _raises(m.interleave_plan, 0, 2); n += 1
    assert "at least one picture" in _raises(m.interleave_plan, 2, 0); n += 1
    assert "when_uneven" in _raises(m.interleave_plan, 2, 2, "cut"); n += 1
    assert m.SYBatchInterleave.RETURN_TYPES == ("IMAGE",); n += 1
    return n
