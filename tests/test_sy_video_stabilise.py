import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_video_stabilise as m


def run():
    n = 0
    # smoothing: window 1 changes nothing, a flat line stays flat, a zig-zag gets calmer
    assert m.smooth_path([1, 5, 2], 1) == [1, 5, 2]
    assert m.smooth_path([4, 4, 4, 4], 5) == [4, 4, 4, 4]
    sm = m.smooth_path([0, 10, 0, 10, 0, 10, 0], 3)
    assert sm[0] == 0 and sm[-1] == 0                       # ends keep their own value
    assert max(sm[1:-1]) - min(sm[1:-1]) < 10
    assert m.smooth_path([], 3) == []
    assert abs(sm[2] - 20.0 / 3) < 1e-9
    n += 6
    # a straight pan is kept: a steady line has no shake to remove
    line = [float(i) for i in range(10)]
    assert m.smooth_path(line, 5) == line
    n += 1
    # wrap of the correlation peak into a signed shift
    assert m.wrap_peak(0, 64) == 0 and m.wrap_peak(3, 64) == 3
    assert m.wrap_peak(61, 64) == -3 and m.wrap_peak(32, 64) == 32
    assert m.shifts_from_peaks([(2, 61)], (64, 64)) == [(-3.0, 2.0)]
    assert m.shifts_from_peaks([(1, 1)], (8, 8), scale=(2.0, 3.0)) == [(2.0, 3.0)]
    n += 5
    # cumulative path and corrections
    assert m.cumulative([(1, 0), (2, 1)]) == [(0.0, 0.0), (1.0, 0.0), (3.0, 1.0)]
    n += 1
    # shake: +5, -5, +5, -5 around a still camera -> corrections cancel most of it
    shake = [(5, 0), (-5, 0), (5, 0), (-5, 0)]
    mv = m.corrections(shake, 5, 80)
    assert len(mv) == 5
    raw = m.cumulative(shake)
    after = [raw[i][0] + mv[i][0] for i in range(5)]
    assert max(after) - min(after) < max(r[0] for r in raw) - min(r[0] for r in raw)
    n += 3
    # still clip: no moves
    assert m.corrections([(0, 0)] * 6, 4, 80) == [(0, 0)] * 7
    # max_shift limits every move
    big = m.corrections([(100, 0), (-100, 0), (100, 0)], 9, 20)
    assert all(abs(dx) <= 20 for dx, _ in big)
    n += 2
    assert m.format_shifts([(1, -2), (0, 0)]) == "1,-2\n0,0"
    assert m.crop_amounts([(3, -1), (-7, 2)]) == (7, 2)
    assert m.crop_amounts([]) == (0, 0)
    n += 3
    # refusal text
    for call in (lambda: m.smooth_path([1, 2], 0), lambda: m.corrections([(1, 1)], 3, 0)):
        try:
            call()
            raise SystemExit("bad args must raise")
        except ValueError as e:
            assert "at least" in str(e)
        n += 1
    assert m.SYVideoStabilise.RETURN_TYPES == ("IMAGE", "STRING")
    n += 1
    return n
