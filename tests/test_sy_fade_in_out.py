import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_fade_in_out as m


def run():
    n = 0

    def ok(cond, msg="check failed"):
        nonlocal n
        n += 1
        if not cond:
            raise SystemExit(msg)

    a = m.fade_amounts(10, 4, 4, "linear")
    ok(len(a) == 10)
    ok(a[0] == 1.0 and a[-1] == 1.0, "first and last frame are fully the colour")
    ok(a[4] == 0.0 and a[5] == 0.0, "middle is untouched")
    ok(a[1] > a[2] > a[3] >= 0.0, "fade in falls")
    ok(a[6] < a[7] < a[8], "fade out rises")
    ok(m.fade_amounts(5, 0, 0, "linear") == [0.0] * 5, "no fades means no change")
    for curve in m.CURVES:
        for cnt, fi, fo in ((10, 30, 30), (3, 12, 12), (1, 5, 5), (20, 0, 7), (20, 7, 0), (2, 300, 1)):
            r = m.fade_amounts(cnt, fi, fo, curve)
            ok(len(r) == cnt and all(0.0 <= v <= 1.0 for v in r), "amounts in 0..1 (%s %s %s %s)" % (curve, cnt, fi, fo))
    e = m.fade_amounts(10, 5, 0, "ease in out")
    ok(e[0] == 1.0 and e[5] == 0.0 and 0.0 < e[2] < 1.0)
    s = m.fade_amounts(10, 30, 10, "linear")
    ok(s[0] == 1.0 and s[-1] == 1.0, "too long fades shrink, never raise")
    for bad in ((0, 1, 1, "linear"), (5, -1, 1, "linear"), (5, 1, 1, "wobble")):
        try:
            m.fade_amounts(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            n += 1
    ok(m.SYFadeInOut.RETURN_TYPES == ("IMAGE",))
    return n
