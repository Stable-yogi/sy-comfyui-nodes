import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_strobe_flash as m


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected ValueError")


def run():
    n = 0
    got = [m.flash_amount(i, 4, 1, 2, 0) for i in range(8)]
    want = [1.0, 2 / 3.0, 1 / 3.0, 0.0, 1.0, 2 / 3.0, 1 / 3.0, 0.0]
    assert all(abs(a - b) < 1e-9 for a, b in zip(got, want)); n += 1
    assert m.flash_amount(0, 4, 1, 2, 0) == 1.0; n += 1
    assert m.flash_amount(3, 4, 1, 2, 0) == 0.0; n += 1
    assert [m.flash_amount(i, 3, 2, 0, 0) for i in range(6)] == [1.0, 1.0, 0.0, 1.0, 1.0, 0.0]; n += 1
    assert [m.flash_amount(i, 5, 1, 0, 2) for i in range(8)] == [0, 0, 1.0, 0, 0, 0, 0, 1.0]; n += 1
    assert m.flash_amount(1, 1, 1, 0, 0) == 1.0; n += 1
    assert abs(m.flash_amount(1, 12, 1, 3, 0) - 0.75) < 1e-9; n += 1
    assert "every_n_frames" in _raises(m.flash_amount, 0, 0, 1, 1, 0); n += 1
    assert "flash_frames" in _raises(m.flash_amount, 0, 4, 0, 1, 0); n += 1
    assert "cannot be negative" in _raises(m.flash_amount, 0, 4, 1, -1, 0); n += 1
    assert "cannot be negative" in _raises(m.flash_amount, 0, 4, 1, 1, -3); n += 1
    assert m.MODES == ["white", "black", "invert", "colour"]; n += 1
    assert m.SYStrobeFlash.RETURN_TYPES == ("IMAGE",); n += 1
    return n
