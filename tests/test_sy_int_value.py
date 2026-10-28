import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_int_value as m


def run():
    assert m.int_value(5) == (5, 5.0)
    assert m.int_value(-3) == (-3, -3.0)
    assert m.int_value(0) == (0, 0.0)
    assert m.int_value(4.0) == (4, 4.0)
    assert m.SYIntValue().run(7) == (7, 7.0)
    for bad in (1.5, True, "3", None, 2 ** 60):
        try:
            m.int_value(bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    assert m.SYIntValue.RETURN_TYPES == ("INT", "FLOAT")
    return 11
