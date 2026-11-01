import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_int_value as m


def run():
    assert m.int_value(5) == (5, 5.0)
    assert m.int_value(-3) == (-3, -3.0)
    assert m.int_value(0) == (0, 0.0)
    assert m.int_value(4.0) == (4, 4.0)
    assert m.SYIntValue().run(7)[:2] == (7, 7.0)
    for bad in (1.5, True, "3", None, 2 ** 60):
        try:
            m.int_value(bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    assert m.SYIntValue.RETURN_TYPES[:2] == ("INT", "FLOAT")
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
    n += ok(m.int_info(1024)[0] == '1024')
    n += ok('multiple of 8, 16, 32, 64' in m.int_info(1024)[1])
    n += ok('not a multiple of 8' in m.int_info(1000 + 1)[1])
    n += ok('4n+1 (fits' in m.int_info(81)[1])
    n += ok('not 4n+1' in m.int_info(80)[1])
    n += ok('odd' in m.int_info(81)[1] and 'even' in m.int_info(80)[1])
    n += ok(m.int_info(-3)[0] == '-3')
    n += ok(rs(m.int_info, 1.5) is not None)
    n += ok(m.SYIntValue().run(7) == (7, 7.0, '7', m.int_info(7)[1]))
    return n
