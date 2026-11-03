import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_overlap_blend as m


def close(a, b):
    return abs(a - b) < 1e-9


def run():
    n = 0
    # normal
    lin = m.blend_weights(3, "linear")
    assert all(close(x, y) for x, y in zip(lin, [0.25, 0.5, 0.75])); n += 1
    sm = m.blend_weights(3, "smooth")
    assert close(sm[1], 0.5) and close(sm[0], 0.0625 * (3 - 0.5)) and sm[0] < 0.25 < 0.75 < sm[2]; n += 1
    ei = m.blend_weights(3, "ease in")
    assert close(ei[0], 0.0625) and close(ei[2], 0.5625); n += 1
    eo = m.blend_weights(3, "ease out")
    assert close(eo[0], 1 - 0.75 ** 2) and close(eo[2], 1 - 0.0625); n += 1
    for c in m.CURVES:
        ws = m.blend_weights(7, c)
        assert len(ws) == 7 and all(0 < x < 1 for x in ws) and ws == sorted(ws)
    n += 1
    # edge: overlap 1 and biggest
    assert close(m.blend_weights(1, "linear")[0], 0.5); n += 1
    assert len(m.blend_weights(1000, "smooth")) == 1000; n += 1
    assert all(0 < x < 1 for x in m.blend_weights(1000, "ease in")); n += 1
    # join length
    assert m.check_join((10, 4, 6, 3), (8, 4, 6, 3), 5) == 13; n += 1
    assert m.check_join((5, 4, 6, 3), (5, 4, 6, 3), 5) == 5; n += 1
    # refusals
    for sa, sb, ov, word in (((10, 4, 6, 3), (8, 4, 6, 3), 9, "Lower overlap_frames to 8"),
                             ((3, 4, 6, 3), (8, 4, 6, 3), 4, "clip_a has 3"),
                             ((10, 4, 6, 3), (8, 5, 6, 3), 2, "6x4 with 3 channels"),
                             ((10, 4, 6, 3), (8, 4, 7, 3), 2, "Resize one"),
                             ((10, 4, 6, 3), (8, 4, 6, 4), 2, "different sizes")):
        try:
            m.check_join(sa, sb, ov)
            raise SystemExit("must raise")
        except ValueError as e:
            assert word in str(e), str(e)
    n += 5
    for bad in ((0, "linear"), (3, "wobble")):
        try:
            m.blend_weights(*bad)
            raise SystemExit("must raise")
        except ValueError:
            pass
    n += 2
    assert m.SYOverlapBlend.RETURN_TYPES == ("IMAGE", "INT"); n += 1
    return n
