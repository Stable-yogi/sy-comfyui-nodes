import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_colour_drift_check as m


def close(a, b):
    return abs(a - b) < 1e-6


def run():
    n = 0
    assert close(m.drift_percent(0.5, 0.55), 10.0); n += 1
    assert close(m.drift_percent(0.5, 0.25), -50.0); n += 1
    assert m.drift_percent(0.0, 0.1) > 1e4; n += 1  # no divide by zero
    assert close(m.pixel_saturation(1.0, 0.5, 0.0), 1.0); n += 1
    assert close(m.pixel_saturation(0.5, 0.5, 0.5), 0.0); n += 1
    assert close(m.pixel_saturation(0, 0, 0), 0.0); n += 1
    b, s = m.frame_stats([(1.0, 0.0, 0.0), (0.5, 0.5, 0.5)])
    assert close(b, (1.0 + 1.5) / 6.0) and close(s, 0.5); n += 2
    # steady
    rep, bc, sc, warn = m.build_report([0.5] * 6, [0.4] * 6, 2, 5)
    assert close(bc, 0) and close(sc, 0) and warn is False and "Verdict: steady" in rep; n += 3
    # more colour only
    rep, bc, sc, warn = m.build_report([0.5] * 6, [0.4, 0.4, 0.4, 0.4, 0.5, 0.5], 2, 5)
    assert close(sc, 25.0) and warn is True and "got more colourful" in rep and "got brighter" not in rep; n += 3
    # both
    rep, bc, sc, warn = m.build_report([0.4, 0.4, 0.5, 0.6], [0.3, 0.3, 0.4, 0.4], 1, 5)
    assert "got brighter and got more colourful" in rep and "+50.0%" in rep; n += 2
    # darker, below threshold stays steady
    rep, bc, sc, warn = m.build_report([0.5, 0.49], [0.4, 0.4], 1, 5)
    assert warn is False and close(bc, -2.0); n += 2
    rep, bc, sc, warn = m.build_report([0.5, 0.2], [0.4, 0.4], 1, 5)
    assert "got darker" in rep and warn is True; n += 2
    # table: at most 12 rows
    rep, *_ = m.build_report([0.5] * 100, [0.4] * 100, 3, 5)
    rows = [ln for ln in rep.split("\n") if ln and ln[0].isdigit() and "|" in ln]
    assert len(rows) == 12 and rows[0].startswith("1 |") and rows[-1].startswith("100 |"); n += 2
    assert m.evenly_spaced(5) == [0, 1, 2, 3, 4]; n += 1
    # edge: exactly two frames, compare 1
    m.build_report([0.5, 0.5], [0.4, 0.4], 1, 5); n += 1
    # refusals
    for args, word in (((1, 1), "at least 2 frames"),
                       ((5, 3), "most you can use is 2"),
                       ((2, 2), "most you can use is 1")):
        try:
            m.check_counts(*args)
            raise SystemExit("must raise")
        except ValueError as e:
            assert word in str(e)
    n += 3
    assert m.SYColourDriftCheck.RETURN_TYPES == ("STRING", "FLOAT", "FLOAT", "BOOLEAN"); n += 1
    return n
