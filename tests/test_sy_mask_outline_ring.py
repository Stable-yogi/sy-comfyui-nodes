import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_outline_ring as m


def _raises(fn, *args, word=""):
    try:
        fn(*args)
    except ValueError as e:
        return word in str(e)
    return False


def run():
    n = 0
    assert m.ring_widths(6, "outside") == (6, 0); n += 1
    assert m.ring_widths(6, "inside") == (0, 6); n += 1
    assert m.ring_widths(6, "centred") == (3, 3); n += 1
    assert m.ring_widths(7, "centred") == (4, 3); n += 1                  # odd pixel goes outside
    assert m.ring_widths(1, "centred") == (1, 0); n += 1
    assert m.ring_widths(200, "centred") == (100, 100); n += 1
    for w in (1, 2, 5, 33, 200):
        for p in m.POSITIONS:
            assert sum(m.ring_widths(w, p)) == w; n += 1                  # the band is always `width` thick
    assert m.round_split(0) == (0, 0); n += 1
    assert m.round_split(10) == (4, 6); n += 1
    assert sum(m.round_split(37)) == 37; n += 1
    assert m.blur_plan(10, 0.0) == (0.0, 1); n += 1
    assert m.blur_plan(4, 1.0) == (2.0, 1); n += 1                        # narrow band: blur at full size
    sigma, shrink = m.blur_plan(100, 1.0)
    assert sigma == 50.0 and shrink == 16; n += 1                         # wide band: blur a shrunken copy
    assert _raises(m.ring_widths, 0, "outside", word="width"); n += 1
    assert _raises(m.ring_widths, 5, "sideways", word="position"); n += 1
    assert _raises(m.check_args, 0, "outside", 0.0, 0.5, word="width"); n += 1
    assert _raises(m.check_args, 201, "outside", 0.0, 0.5, word="width"); n += 1
    assert _raises(m.check_args, 5, "middle", 0.0, 0.5, word="position"); n += 1
    assert _raises(m.check_args, 5, "inside", 1.5, 0.5, word="soft"); n += 1
    assert _raises(m.check_args, 5, "inside", 0.5, -1, word="threshold"); n += 1
    assert m.SYMaskOutlineRing.RETURN_TYPES == ("MASK",); n += 1
    return n
