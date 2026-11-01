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
    assert m.SYCounter().run(4, 0, 1, 3, True)[0] == 0
    for bad in ((-1, 0, 1, 3), (1.5, 0, 1, 3), (True, 0, 1, 3), (0, 0, 1, -1), (0, "a", 1, 3)):
        try:
            c(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    assert c(0, 0, 1, -1, False) == 0                                     # max ignored when wrap is off
    # new: lap and info
    assert m.counter_details(0, 0, 1, 3) == (0, 0, "Run 0: 0 + 1 x 0 = 0 (inside 0..3)")
    assert m.counter_details(5, 0, 1, 3)[:2] == (1, 1)
    assert "wrapped into 0..3 -> 1 (round 2)" in m.counter_details(5, 0, 1, 3)[2]
    assert [m.counter_details(i, 0, 1, 3)[1] for i in range(9)] == [0, 0, 0, 0, 1, 1, 1, 1, 2]
    assert m.counter_details(5, 10, 1, 12, False) == (15, 0, "Run 5: 10 + 1 x 5 = 15")
    assert m.counter_details(2, 10, -1, 12)[:2] == (11, 0)
    assert m.SYCounter().run(7, 0, 1, 3, True)[:2] == (3, 1)
    try:
        m.counter_details(0, 5, 1, 2)
        raise SystemExit("must raise")
    except ValueError as e:
        assert "max_value" in str(e) and "wrap" in str(e)
    assert m.SYCounter.RETURN_TYPES == ("INT", "INT", "STRING") and len(m.SYCounter.RETURN_NAMES) == 3
    return 27
