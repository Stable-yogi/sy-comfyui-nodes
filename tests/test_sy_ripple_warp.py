import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_ripple_warp as m
import _sy_ae_common as ae


def run():
    n = 0
    # strength 0: no move at all
    for c in (0, 17.5, 999):
        assert m.ripple_offset(c, 120, 33, 0.0) == 0.0
        n += 1
    # normal: quarter wave gives the full strength, half wave gives about zero
    assert abs(m.ripple_offset(30, 120, 0, 8.0) - 8.0) < 1e-9
    assert abs(m.ripple_offset(60, 120, 0, 8.0)) < 1e-9
    n += 2
    # phase 90 degrees moves the crest to coord 0
    assert abs(m.ripple_offset(0, 120, 90, 5.0) - 5.0) < 1e-9
    n += 1
    # repeats every wavelength; never exceeds the strength
    assert abs(m.ripple_offset(10, 50, 20, 7.0) - m.ripple_offset(60, 50, 20, 7.0)) < 1e-9
    assert all(abs(m.ripple_offset(c, 4, 0, 100.0)) <= 100.0 + 1e-9 for c in range(0, 50))
    n += 2
    # refusals
    for bad in (0, -5):
        try:
            m.ripple_offset(1, bad, 0, 1)
            raise SystemExit("expected ValueError")
        except ValueError as e:
            assert "wavelength" in str(e)
    n += 2
    try:
        ae.check_shape(())
        raise SystemExit("expected ValueError")
    except ValueError:
        pass
    n += 1
    d = m.SYRippleWarp.INPUT_TYPES()["required"]
    assert d["wavelength"][1]["default"] == 120.0 and d["strength_x"][1]["default"] == 8.0
    n += 1
    return n
