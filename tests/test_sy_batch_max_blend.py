import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_batch_max_blend as m


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected ValueError")


def run():
    n = 0
    assert m.decay_factor(0.0) == 1.0; n += 1
    assert m.decay_factor(1.0) == 0.0; n += 1
    assert abs(m.decay_factor(0.25) - 0.75) < 1e-12; n += 1
    assert "between 0 and 1" in _raises(m.decay_factor, 1.5); n += 1
    assert "between 0 and 1" in _raises(m.decay_factor, -0.1); n += 1
    assert m.used_range(6, 0, 0) == (0, 6); n += 1
    assert m.used_range(6, 2, 2) == (2, 4); n += 1
    assert m.used_range(6, 4, 9) == (4, 6); n += 1
    assert "Lower start" in _raises(m.used_range, 6, 6, 1); n += 1
    assert "no pictures" in _raises(m.used_range, 0, 0, 0); n += 1
    assert m.OUTPUTS == ["last frame of trail", "every step"]; n += 1
    assert m.SYBatchMaxBlend.RETURN_TYPES == ("IMAGE",); n += 1
    return n
