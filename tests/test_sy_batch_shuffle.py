import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_batch_shuffle as m


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected ValueError")


def run():
    n = 0
    # generator matches the published first output of splitmix64 for seed 0
    assert next(m._stream(0)) == 0xE220A8397B1DCDAF; n += 1
    # fixed expected orders (same on every machine)
    assert m.shuffle_order(4, 0) == [2, 1, 0, 3]; n += 1
    assert m.shuffle_order(4, 1) == [2, 0, 3, 1]; n += 1
    assert m.shuffle_order(5, 123) == [3, 2, 1, 4, 0]; n += 1
    assert m.shuffle_order(10, 2 ** 53) == [4, 8, 9, 5, 3, 1, 0, 2, 6, 7]; n += 1
    # edge: one picture, two pictures, biggest batch is a full permutation
    assert m.shuffle_order(1, 99) == [0]; n += 1
    assert sorted(m.shuffle_order(2, 7)) == [0, 1]; n += 1
    big = m.shuffle_order(5000, 5)
    assert sorted(big) == list(range(5000)) and big != list(range(5000)); n += 1
    # same seed same order, global random state untouched
    random.seed(1)
    before = random.random()
    random.seed(1)
    a = m.shuffle_order(20, 3)
    assert random.random() == before; n += 1
    assert a == m.shuffle_order(20, 3) and a != m.shuffle_order(20, 4); n += 1
    # refusals
    assert "batch is empty" in _raises(m.shuffle_order, 0, 1); n += 1
    assert "seed must be" in _raises(m.shuffle_order, 3, -1); n += 1
    assert m.SYBatchShuffle.RETURN_TYPES == ("IMAGE", "STRING"); n += 1
    return n
