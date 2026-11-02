import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_deflicker as m


def run():
    n = 0

    def ok(cond, msg="check failed"):
        nonlocal n
        n += 1
        if not cond:
            raise SystemExit(msg)

    flat = [0.5] * 6
    ok(m.smooth_targets(flat, 3) == flat)
    spike = [0.4, 0.4, 0.4, 0.8, 0.4, 0.4, 0.4]
    t = m.smooth_targets(spike, 1)
    ok(abs(t[3] - (0.4 + 0.8 + 0.4) / 3) < 1e-9, "spike average with window 1")
    ok(t[0] == 0.4, "edge uses fewer neighbours")
    g = m.gains_for(spike, 2, 1.0)
    ok(g[3] < 1.0, "bright spike is pulled down")
    ok(g[2] > 1.0, "neighbour of the spike is lifted")
    ok(all(0.5 <= v <= 2.0 for v in g), "gains stay clamped")
    ok(m.gains_for(spike, 1, 1.0) == [1.0] * 7, "window 1 changes nothing")
    ok(m.gains_for(spike, 5, 0.0) == [1.0] * 7, "strength 0 changes nothing")
    half = m.gains_for(spike, 2, 0.5)
    ok(abs((half[3] - 1.0) - (g[3] - 1.0) / 2) < 1e-9, "strength 0.5 is half the correction")
    ok(m.gains_for([0.0, 0.5, 0.0], 1, 1.0) == [1.0, 1.0, 1.0])
    ok(m.gains_for([0.0, 0.5, 0.2], 2, 1.0)[0] == 1.0, "a black frame is left alone")
    try:
        m.gains_for(spike, 2, 1.5)
        raise SystemExit("bad strength must raise")
    except ValueError:
        n += 1
    try:
        m.smooth_targets(spike, 0)
        raise SystemExit("bad window must raise")
    except ValueError:
        n += 1
    ok(m.deflicker_info([1.0, 0.8, 1.05]) == "Biggest correction: 20.0 percent")
    ok(m.deflicker_info([]) == "Biggest correction: 0.0 percent")
    ok(m.SYDeflicker.RETURN_TYPES == ("IMAGE", "STRING"))
    return n
