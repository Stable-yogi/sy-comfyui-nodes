import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_counter as m


def run():
    c = m.counter_value
    assert [c(i, 0, 1, 3) for i in range(6)] == [0, 1, 2, 3, 0, 1]
    assert [c(i, 5, 2, 10) for i in range(5)] == [5, 7, 9, 5, 7]
    assert [c(i, 10, 1, 12, False) for i in range(4)] == [10, 11, 12, 13]
    assert [c(i, 10, -1, 12) for i in range(5)] == [10, 12, 11, 10, 12]   # counts down, wraps up
    assert [c(i, 0, -3, 0, False) for i in range(3)] == [0, -3, -6]
    assert c(100, 7, 1, 7) == 7                                           # one-value range
    assert c(0, -4, 1, 4) == -4
    assert c(9, -4, 1, 4) == -4
    assert c(3, 0, 0, 5) == 0                                             # step 0 never moves
    assert m.SYCounter().run(4, 0, 1, 3, True) == (0,)
    for bad in ((-1, 0, 1, 3), (1.5, 0, 1, 3), (True, 0, 1, 3), (0, 0, 1, -1), (0, "a", 1, 3)):
        try:
            c(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    assert c(0, 0, 1, -1, False) == 0                                     # max ignored when wrap is off
    assert m.SYCounter.RETURN_TYPES == ("INT",)
    return 17
