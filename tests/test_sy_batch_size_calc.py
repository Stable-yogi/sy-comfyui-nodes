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


def raises_info(*args):
    try:
        m.batch_info(*args)
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
    assert m.SYBatchSizeCalc().run(10, 4)[:3] == (3, 2, 2); n += 1
    # added value: pass_size and the info text
    assert m.batch_info(10, 4) == (4, "10 pictures, at most 4 per run -> 3 runs: 4 + 4 + 2. The last run is shorter (2)."); n += 1
    assert m.batch_info(8, 4) == (4, "8 pictures, at most 4 per run -> 2 runs: 4 + 4. Every run is full."); n += 1
    assert m.batch_info(3, 4) == (3, "3 pictures, at most 4 per run -> 1 run: 3. Everything fits in one run."); n += 1
    assert m.batch_info(0, 4) == (0, "Total is 0: nothing to render."); n += 1
    assert m.batch_info(1, 1)[0] == 1; n += 1
    size, info = m.batch_info(10_000_000, 3)
    assert size == 3 and "3333333 runs of 3, then 1 run of 1" in info; n += 1
    assert m.pass_sizes_text(200, 10) == "20 runs of 10" and m.pass_sizes_text(205, 10) == "20 runs of 10, then 1 run of 5"; n += 1
    assert m.pass_sizes_text(0, 3) == "no runs (nothing to do)"; n += 1
    out = m.SYBatchSizeCalc().run(10, 4)
    assert out[3] == 4 and out[4].startswith("10 pictures") and len(out) == 5; n += 1
    assert m.SYBatchSizeCalc.RETURN_TYPES == ("INT", "INT", "INT", "INT", "STRING"); n += 1
    assert m.SYBatchSizeCalc.RETURN_NAMES[:3] == ("passes", "last_pass_size", "remainder"); n += 1
    assert raises_info(-1, 4) and raises_info(5, 0); n += 1
    return n
