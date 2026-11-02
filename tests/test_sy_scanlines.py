import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_scanlines as m


def _raises(fn, *args, word=""):
    try:
        fn(*args)
    except ValueError as e:
        return word in str(e)
    return False


def run():
    n = 0
    f = m.line_factor
    assert abs(f(0, 3, 0.35, 0) - 0.65) < 1e-9; n += 1          # middle of a dark line
    assert abs(f(3, 3, 0.35, 0) - 0.65) < 1e-9; n += 1          # repeats every line_gap
    assert abs(f(4, 4, 0.5, 2) - f(0, 4, 0.5, 2)) < 1e-9; n += 1
    assert abs(f(2, 4, 0.5, 0) - 1.0) < 1e-9; n += 1             # halfway between lines is untouched (gap 4)
    assert abs(f(1, 2, 0.4, 0) - 1.0) < 1e-9; n += 1             # smallest gap, bright row
    assert f(0, 16, 1.0, 0) == 0.0; n += 1                       # full darkness
    for r in range(20):
        assert f(r, 5, 0.0, 3) == 1.0                            # darkness 0 = identical
        assert 0.7 - 1e-9 <= f(r, 5, 0.3, 3) <= 1.0
    n += 2
    assert 0.0 < f(1, 5, 0.5, 0) < 1.0 and f(1, 5, 0.5, 0) != 0.5; n += 1   # smooth, not a hard step
    assert abs(f(0.5, 4, 0.5, 0) - f(0, 4, 0.5, 0)) > 1e-6; n += 1          # fractional rows work (wobble)
    assert _raises(f, 0, 1, 0.3, 0, word="line_gap"); n += 1
    assert _raises(f, 0, 3, 1.5, 0, word="darkness"); n += 1
    assert _raises(f, 0, 3, 0.3, -1, word="offset"); n += 1
    assert _raises(m.check_args, 3, 0.3, -1.0, 0, word="wobble"); n += 1
    assert m.SYScanlines.RETURN_TYPES == ("IMAGE",); n += 1
    assert list(m.SYScanlines.INPUT_TYPES()["required"]) == ["image", "line_gap", "darkness", "wobble", "offset"]; n += 1
    return n
