import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_float_value as m


def run():
    assert m.float_value(1.5) == (1.5, 2)
    assert m.float_value(-1.5) == (-1.5, -2)
    assert m.float_value(2.4) == (2.4, 2)
    assert m.float_value(3) == (3.0, 3)
    assert m.float_value(0.0) == (0.0, 0)
    assert m.SYFloatValue().run(0.25)[:2] == (0.25, 0)
    for bad in (float("nan"), float("inf"), True, "1", None, 1e20):
        try:
            m.float_value(bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    assert m.SYFloatValue.RETURN_TYPES[:2] == ("FLOAT", "INT")
    return 12 + _extra(m)


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
    n += ok(m.float_info(2.5)[0] == '2.5')
    n += ok(m.float_info(3.0)[0] == '3')
    n += ok('rounded down 2' in m.float_info(2.5)[1] and 'rounded up 3' in m.float_info(2.5)[1])
    n += ok('rounded down -3' in m.float_info(-2.5)[1] and 'nearest whole -3' in m.float_info(-2.5)[1])
    n += ok(rs(m.float_info, float('nan')) is not None)
    n += ok(m.SYFloatValue().run(1.5)[2] == '1.5')
    return n
