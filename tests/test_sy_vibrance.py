import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_vibrance as m
import _sy_ae_common as ae


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        assert str(e)
        return True
    raise SystemExit("expected ValueError")


def run():
    n = 0
    # normal: dull colours get more lift than strong ones
    assert m.vibrance_gain(0.1, 0.4) > m.vibrance_gain(0.9, 0.4) > 1.0
    n += 1
    # edge: full saturation gets almost no lift, zero amount is neutral
    assert abs(m.vibrance_gain(1.0, 1.0) - 1.0) < 1e-9
    assert m.vibrance_gain(0.3, 0.0) == 1.0
    n += 2
    # negative amount mutes, never goes below zero
    assert 0.0 <= m.vibrance_gain(0.0, -1.0) < 1.0
    assert m.vibrance_gain(1.0, -1.0) == 1.0
    n += 2
    # skin tones are protected a little
    assert m.vibrance_gain(0.3, 0.5, skin=1.0) < m.vibrance_gain(0.3, 0.5, skin=0.0)
    assert m.skin_weight(30) == 1.0 and m.skin_weight(200) == 0.0 and m.skin_weight(375) == 1.0
    n += 2
    # refusals
    _raises(m.vibrance_gain, 1.5, 0.4)
    _raises(m.vibrance_gain, 0.5, 2.0)
    _raises(ae.check_shape, (4, 4))
    _raises(ae.check_shape, (1, 0, 4, 3))
    _raises(ae.check_shape, (1, 4, 4, 1))
    n += 5
    assert ae.check_shape((4, 5, 3)) == (1, 4, 5, 3)
    n += 1
    assert m.SYVibrance.RETURN_TYPES == ("IMAGE",)
    assert m.SYVibrance.INPUT_TYPES()["required"]["amount"][1]["default"] == 0.4
    n += 2
    return n
