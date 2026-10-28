import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_batch_size_calc as m


def _raises(*args):
    try:
        m.calc_passes(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.calc_passes(10, 4) == (3, 2, 2); n += 1
    assert m.calc_passes(8, 4) == (2, 4, 0); n += 1
    assert m.calc_passes(3, 4) == (1, 3, 3); n += 1
    assert m.calc_passes(4, 4) == (1, 4, 0); n += 1
    assert m.calc_passes(1, 1) == (1, 1, 0); n += 1
    assert m.calc_passes(0, 4) == (0, 0, 0); n += 1  # zero total
    assert m.calc_passes(5, 1000) == (1, 5, 5); n += 1
    assert m.calc_passes(10_000_000, 3) == (3333334, 1, 1); n += 1  # huge
    for total in range(0, 40):
        for mx in range(1, 9):
            p, last, rem = m.calc_passes(total, mx)
            assert (p - 1) * mx + last == total if total else p == 0
            n += 1
    for bad in ((-1, 4), (5, 0), (5, -2), (10_000_001, 4)):
        assert _raises(*bad), bad
        n += 1
    assert m.SYBatchSizeCalc().run(10, 4) == (3, 2, 2); n += 1
    return n
