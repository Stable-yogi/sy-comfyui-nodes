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
    assert m.SYFloatValue().run(0.25) == (0.25, 0)
    for bad in (float("nan"), float("inf"), True, "1", None, 1e20):
        try:
            m.float_value(bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    assert m.SYFloatValue.RETURN_TYPES == ("FLOAT", "INT")
    return 12
