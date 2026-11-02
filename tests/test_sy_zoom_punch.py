import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_zoom_punch as m


def run():
    n = 0
    assert m.parse_frames("12, 30, 48", 100) == [12, 30, 48]
    assert m.parse_frames("", 10) == []
    assert m.parse_frames("   ", 10) == []
    assert m.parse_frames("5 3;3,1", 10) == [1, 3, 5]
    assert m.parse_frames(None, 10) == []
    n += 5
    for text, count, word in (("a, 3", 10, "not a number"), ("2.5", 10, "not a number"), ("-1", 10, "negative"),
                              ("10", 10, "does not exist"), ("3, 99", 10, "99")):
        try:
            m.parse_frames(text, count)
            raise SystemExit("bad frames must raise")
        except ValueError as e:
            assert word in str(e)
        n += 1
    assert m.pulse(0, 8) == 1.0
    assert m.pulse(-1, 8) == 0.0 and m.pulse(8, 8) == 0.0 and m.pulse(50, 8) == 0.0
    assert 0.0 < m.pulse(4, 8) < m.pulse(2, 8) < 1.0
    n += 3
    try:
        m.pulse(0, 0)
        raise SystemExit("length 0 must raise")
    except ValueError as e:
        assert "at least" in str(e)
    n += 1
    f = m.zoom_factors(10, [2], 0.2, 4)
    assert len(f) == 10 and f[0] == 1.0 and f[1] == 1.0 and abs(f[2] - 1.2) < 1e-9
    assert f[2] > f[3] > f[4] > f[5] >= 1.0 and f[6] == 1.0
    assert m.zoom_factors(5, [], 0.5, 4) == [1.0] * 5            # no hits: no change
    # overlapping pulses take the maximum, never add up
    g = m.zoom_factors(10, [2, 3], 0.2, 4)
    assert abs(g[3] - 1.2) < 1e-9 and max(g) <= 1.2 + 1e-9
    assert m.zoom_factors(3, [0], 0.0, 4) == [1.0] * 3
    n += 5
    try:
        m.zoom_factors(3, [0], 1.5, 4)
        raise SystemExit("strength 1.5 must raise")
    except ValueError as e:
        assert "strength must be" in str(e)
    assert m.SYZoomPunch.RETURN_TYPES == ("IMAGE",)
    n += 2
    return n
