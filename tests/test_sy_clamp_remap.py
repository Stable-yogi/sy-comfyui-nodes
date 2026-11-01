import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_clamp_remap as m


def close(a, b):
    return math.isclose(a[0], b[0], abs_tol=1e-9) and math.isclose(a[1], b[1], abs_tol=1e-9)


def run():
    assert close(m.clamp_remap(0.5, 0, 1, 0, 100), (50.0, 0.5))
    assert close(m.clamp_remap(2.0, 0, 1, 0, 100), (100.0, 1.0))
    assert close(m.clamp_remap(-1.0, 0, 1, 0, 100), (0.0, 0.0))
    assert close(m.clamp_remap(2.0, 0, 1, 0, 100, clamp=False), (200.0, 1.0))
    assert close(m.clamp_remap(0.25, 0, 1, 10, 0), (7.5, 0.25))          # reversed output
    assert close(m.clamp_remap(0.25, 1, 0, 0, 100), (75.0, 0.25))        # reversed input
    assert close(m.clamp_remap(5, 1, 0, 0, 100), (0.0, 1.0))             # reversed input, clamped
    assert close(m.clamp_remap(15, 10, 20, -1, 1), (0.0, 15.0))
    assert close(m.SYClampRemap().run(0.5, 0, 1, 0, 8, True)[:2], (4.0, 0.5))
    for bad in ((1, 2, 2, 0, 1), (float("nan"), 0, 1, 0, 1), ("x", 0, 1, 0, 1), (True, 0, 1, 0, 1), (1, 0, float("inf"), 0, 1)):
        try:
            m.clamp_remap(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    assert m.SYClampRemap.RETURN_TYPES[:2] == ("FLOAT", "FLOAT")
    return 15 + _extra(m)


def _extra(m):
    n = 0
    def ok(c):
        assert c
        return 1
    def rs(fn, *a, **k):
        try:
            fn(*a, **k)
        except ValueError as e:
            return str(e)
        return None
    n += ok(m.remap_info(0.5, 0, 1, 0, 8)[0] is False)
    n += ok(m.remap_info(2, 0, 1, 0, 8)[0] is True)
    n += ok('held at 1' in m.remap_info(2, 0, 1, 0, 8)[1])
    n += ok('clamp is off' in m.remap_info(2, 0, 1, 0, 8, False)[1])
    n += ok(m.remap_info(-1, 1, 0, 0, 8)[0] is True)
    n += ok(rs(m.remap_info, 1, 3, 3, 0, 1) is not None)
    n += ok(m.SYClampRemap().run(2, 0, 1, 0, 8, True)[2] is True)
    return n
