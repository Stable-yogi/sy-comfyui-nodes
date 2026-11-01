import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import _sy_d1_finish as f


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    assert f.check_mix(0.0) is None and f.check_mix(1.0) is None; n += 1
    assert "mix" in raises(f.check_mix, 1.5); n += 1
    assert "mix" in raises(f.check_mix, -0.1); n += 1
    assert f.blend_value(0.2, 0.8, 0.0) == 0.2; n += 1
    assert f.blend_value(0.2, 0.8, 1.0) == 0.8; n += 1
    assert abs(f.blend_value(0.2, 0.8, 0.5) - 0.5) < 1e-9; n += 1
    assert f.blend_value(0.9, 2.0, 1.0) == 1.0 and f.blend_value(0.1, -2.0, 1.0) == 0.0; n += 1
    assert f.check_mask_batch(1, 4) is None and f.check_mask_batch(4, 4) is None; n += 1
    assert "mask" in raises(f.check_mask_batch, 3, 4); n += 1
    t = f.info_line("Sepia", False, 0.5, True)
    assert "switched off" in t and "unchanged" in t; n += 1
    t = f.info_line("Sepia", True, 0.5, True, "strength 2")
    assert "strength 2" in t and "mix 50%" in t and "inside the mask only" in t; n += 1
    assert "whole picture" in f.info_line("X", True, 1.0, False); n += 1
    for tip in (f.MASK_TIP, f.MIX_TIP, f.ENABLED_TIP):
        assert 1 <= len(tip) <= 120; n += 1
    return n
