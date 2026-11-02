import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_bloom as m


def bad(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.bright_weight(0.0, 0.7) == 0.0; n += 1
    assert m.bright_weight(1.0, 0.7) == 1.0; n += 1
    assert abs(m.bright_weight(0.7, 0.7) - 0.5) < 1e-9; n += 1
    a, b = m.bright_weight(0.65, 0.7), m.bright_weight(0.75, 0.7)
    assert 0.0 < a < 0.5 < b < 1.0; n += 1
    assert m.bright_weight(0.5, 0.0) > 0.9; n += 1  # threshold 0: nearly everything glows
    assert bad(m.bright_weight, 0.5, 1.5); n += 1
    w = m.gaussian_weights(5)
    assert len(w) == 11 and abs(sum(w) - 1.0) < 1e-9 and w[5] == max(w) and abs(w[0] - w[10]) < 1e-12; n += 1
    assert len(m.gaussian_weights(1)) == 3; n += 1
    assert bad(m.gaussian_weights, 0); n += 1
    assert m.SYBloom.RETURN_NAMES == ("image",); n += 1
    assert "tint" in m.SYBloom.INPUT_TYPES()["required"]; n += 1
    return n  # checks
