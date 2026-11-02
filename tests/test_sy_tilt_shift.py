import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_tilt_shift as m


def bad(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.blur_amount(0.5, 0.5, 0.2, 12) == 0.0; n += 1
    assert m.blur_amount(0.59, 0.5, 0.2, 12) == 0.0; n += 1  # inside the band
    assert m.blur_amount(1.0, 0.5, 0.2, 12) == 12.0; n += 1  # far edge: full blur
    assert m.blur_amount(0.0, 0.5, 0.2, 12) == 12.0; n += 1
    a, b = m.blur_amount(0.7, 0.5, 0.2, 12), m.blur_amount(0.9, 0.5, 0.2, 12)
    assert 0.0 < a < b < 12.0; n += 1
    assert m.blur_amount(0.9, 0.5, 0.2, 0) == 0.0; n += 1
    assert m.blur_amount(0.5, 0.5, 0.0, 12) == 0.0 and m.blur_amount(0.6, 0.5, 0.0, 12) > 0; n += 1
    assert m.blur_amount(0.3, 0.0, 0.0, 10) > 0; n += 1  # band at the very top
    assert m.blur_amount(0.5, 0.5, 1.0, 10) == 0.0; n += 1  # band covers everything
    assert bad(m.blur_amount, 0.5, 1.2, 0.2, 5); n += 1
    assert bad(m.blur_amount, 0.5, 0.5, -0.2, 5); n += 1
    assert bad(m.blur_amount, 0.5, 0.5, 0.2, -5); n += 1
    r = m.level_radii(8)
    assert len(r) == 5 and r[0] == 0 and r[-1] == 8 and r[2] == 4; n += 1
    assert m.mix_position(0, 8) == (0, 0.0); n += 1
    assert m.mix_position(8, 8) == (3, 1.0); n += 1
    lo, f = m.mix_position(3, 8)
    assert lo == 1 and abs(f - 0.5) < 1e-9; n += 1
    assert m.mix_position(5, 0) == (0, 0.0); n += 1
    w = m.gaussian_weights(4)
    assert len(w) == 9 and abs(sum(w) - 1.0) < 1e-9; n += 1
    assert bad(m.gaussian_weights, 0); n += 1
    assert "vertical" in m.SYTiltShift.INPUT_TYPES()["required"]; n += 1
    return n  # checks
