import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_bool_value as m


def run():
    assert m.bool_value(True) == (True, 1)
    assert m.bool_value(False) == (False, 0)
    assert m.SYBoolValue().run(True)[:2] == (True, 1)
    for bad in (1, 0, "yes", None):
        try:
            m.bool_value(bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    assert m.SYBoolValue.RETURN_TYPES[:2] == ("BOOLEAN", "INT")
    return 8 + _extra(m)


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
    n += ok(m.bool_extras(True)[0] is False)
    n += ok(m.bool_extras(False)[0] is True)
    n += ok('yes' in m.bool_extras(True)[1] and 'no' in m.bool_extras(True)[1])
    n += ok(m.SYBoolValue().run(False) == (False, 0, True, m.bool_extras(False)[1]))
    n += ok(m.SYBoolValue.RETURN_TYPES[2:] == ('BOOLEAN', 'STRING'))
    n += ok(len(m.SYBoolValue.RETURN_TYPES) == len(m.SYBoolValue.RETURN_NAMES))
    n += ok(rs(m.bool_extras, 'x') is not None)
    return n
