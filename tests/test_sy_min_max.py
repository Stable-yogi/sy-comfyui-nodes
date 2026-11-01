import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_min_max as m


def run():
    assert m.min_max(1, 2) == (1.0, 2.0)
    assert m.min_max(5, -3) == (-3.0, 5.0)
    assert m.min_max(2.5, 2.5) == (2.5, 2.5)
    assert m.min_max(-1, -2) == (-2.0, -1.0)
    assert m.SYMinMax().run(9.0, 4.0)[:2] == (4.0, 9.0)
    for bad in ((float("nan"), 1), (1, float("inf")), ("a", 1), (True, 1), (None, 1)):
        try:
            m.min_max(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    assert m.SYMinMax.RETURN_TYPES[:2] == ("FLOAT", "FLOAT")
    return 11 + _extra(m)


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
    n += ok(m.min_max_info(9, 4)[0] is True)
    n += ok(m.min_max_info(4, 9)[0] is False)
    n += ok(m.min_max_info(5, 5) == (False, 'a and b are equal (5)'))
    n += ok('min 4, max 9' in m.min_max_info(9, 4)[1])
    n += ok(m.SYMinMax().run(9.0, 4.0)[2] is True)
    n += ok(rs(m.min_max_info, 'x', 1) is not None)
    return n
