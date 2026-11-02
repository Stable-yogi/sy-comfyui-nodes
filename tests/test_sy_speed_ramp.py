import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_speed_ramp as m


def run():
    n = 0

    def ok(cond, msg="check failed"):
        nonlocal n
        n += 1
        if not cond:
            raise SystemExit(msg)

    p = m.ramp_positions(48, 2.0, 2.0, "linear")
    ok(len(p) == 24, "constant speed 2 should give 24 frames, got %d" % len(p))
    ok(p[0] == 0.0 and p[1] == 2.0)
    p1 = m.ramp_positions(10, 1.0, 1.0, "linear")
    ok(p1 == [float(i) for i in range(10)], "speed 1 keeps every frame")
    for curve in m.CURVES:
        pos = m.ramp_positions(60, 0.5, 4.0, curve)
        ok(all(b >= a for a, b in zip(pos, pos[1:])), "positions must never decrease (%s)" % curve)
        ok(all(0.0 <= v <= 59.0 for v in pos), "positions must stay inside 0..count-1 (%s)" % curve)
    slow = m.ramp_positions(48, 0.5, 0.5, "linear")
    ok(len(slow) > 48, "half speed gives more frames")
    ramp = m.ramp_positions(48, 1.0, 2.0, "linear")
    ok(31 <= len(ramp) <= 36, "ramp 1 to 2 length is sensible, got %d" % len(ramp))
    for bad in ((1, 1.0, 1.0, "linear"), (10, 0.0, 1.0, "linear"), (10, 1.0, 9.0, "linear"), (10, 1.0, 1.0, "wobble")):
        try:
            m.ramp_positions(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            n += 1
    ok(m.ramp_info(48, 31, 1.0, 2.0) == "48 frames -> 31 frames, speed 1.0 to 2.0")
    ok(m.SYSpeedRamp.RETURN_TYPES == ("IMAGE", "STRING"))
    return n
