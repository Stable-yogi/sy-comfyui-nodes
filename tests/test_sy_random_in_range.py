import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_random_in_range as m


def run():
    a = m.random_in_range(42, 0, 100)
    assert a == m.random_in_range(42, 0, 100)               # repeatable
    assert a != m.random_in_range(43, 0, 100)               # seed changes it
    assert isinstance(a[0], int) and isinstance(a[1], float)
    for s in range(200):
        i, f = m.random_in_range(s, -5, 5)
        assert -5 <= i <= 5 and -5.0 <= f <= 5.0
    seen = {m.random_in_range(s, 1, 3)[0] for s in range(100)}
    assert seen == {1, 2, 3}                                 # both ends included
    assert m.random_in_range(7, 4, 4) == (4, 4.0)            # empty range
    i, f = m.random_in_range(1, 0.2, 0.8)                    # no whole number inside
    assert 0.2 <= f <= 0.8 and i == round(f)
    i, f = m.random_in_range(2 ** 64 - 1, 0, 10)
    assert 0 <= i <= 10
    assert m.SYRandomInRange().run(5, 0, 10) == m.random_in_range(5, 0, 10)
    for bad in ((-1, 0, 1), (1.5, 0, 1), (True, 0, 1), (1, 5, 1), (1, float("nan"), 1), (1, "a", 2)):
        try:
            m.random_in_range(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    assert m.SYRandomInRange.RETURN_TYPES == ("INT", "FLOAT")
    return 18
