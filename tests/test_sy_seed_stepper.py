import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_seed_stepper as m


def run():
    s, lst = m.step_seeds(10, 5, 4, 2)
    assert s == 20 and lst == [10, 15, 20, 25]
    assert m.step_seeds(10, 5, 4, 5)[0] == 15  # wraps 5 -> 1
    assert m.step_seeds(0, -1, 3, 1)[0] == m.MAX_SEED  # below zero wraps around
    assert m.seed_at(m.MAX_SEED, 1, 1) == 0
    for bad in ((1, 1, 0, 0, True), (1, 1, 3, 3, False), (1, 1, 3, -1, True)):
        try:
            m.step_seeds(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError:
            pass
    out = m.SYSeedStepper().run(100, 10, 3, 1, True)
    assert out[:2] == (110, "100, 110, 120")
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYSeedStepper"] == "Seed Stepper SY"
    return 9 + _extra(m)


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
    n += ok(m.used_index(4, 1) == 1)
    n += ok(m.used_index(4, 6) == 2)
    n += ok('outside the list' in rs(m.used_index, 4, 6, False))
    n += ok(rs(m.used_index, 0, 0) is not None)
    n += ok(m.SYSeedStepper().run(100, 10, 3, 4, True)[2] == 1)
    n += ok('wrapped to 1' in m.SYSeedStepper().run(100, 10, 3, 4, True)[3])
    n += ok('wrapped' not in m.SYSeedStepper().run(100, 10, 3, 1, True)[3])
    n += ok(m.SYSeedStepper().run(100, 10, 3, 1, True)[0] == 110)
    return n
