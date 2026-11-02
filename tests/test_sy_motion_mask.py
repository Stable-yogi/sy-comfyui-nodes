import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_motion_mask as m


def run():
    n = 0
    assert m.diff_to_mask([0.0, 0.07, 0.08, 0.5], 0.08) == [0.0, 0.0, 1.0, 1.0]
    assert m.diff_to_mask([], 0.5) == []
    assert m.diff_to_mask([0.0, 0.2], 0.0) == [1.0, 1.0]
    assert m.diff_to_mask([1.0], 1.0) == [1.0]
    n += 4
    assert m.reference_index(0, "previous frame") is None
    assert m.reference_index(0, "first frame") is None
    assert m.reference_index(5, "previous frame") == 4
    assert m.reference_index(5, "first frame") == 0
    n += 4
    k = m.gauss_kernel(2.0)
    assert abs(sum(k) - 1.0) < 1e-9 and len(k) == 13 and k[6] == max(k)
    assert m.gauss_kernel(0) == [1.0]
    n += 3
    for bad in ((1.5, 3, 2, "previous frame"), (-0.1, 3, 2, "previous frame"), (0.1, 51, 2, "previous frame"),
                (0.1, 3, -1, "previous frame"), (0.1, 3, 2, "next frame")):
        try:
            m.check_args(*bad)
            raise SystemExit("bad args must raise")
        except ValueError as e:
            assert "must be" in str(e)
        n += 1
    m.check_args(0.08, 3, 2, "first frame")
    assert m.SYMotionMask.RETURN_TYPES == ("MASK",)
    n += 2
    return n
