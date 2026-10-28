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
    assert out == (110, "100, 110, 120")
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYSeedStepper"] == "Seed Stepper SY"
    return 9
