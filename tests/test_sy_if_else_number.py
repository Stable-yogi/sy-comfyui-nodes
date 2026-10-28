import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_if_else_number as m


def run():
    assert m.if_else_number(True, 1.5, 9) == (1.5, 2)
    assert m.if_else_number(False, 1.5, 9) == (9.0, 9)
    assert m.if_else_number(False, 0, -2.5) == (-2.5, -3)
    assert m.SYIfElseNumber().run(True, 3.0, 4.0) == (3.0, 3)
    for bad in ((1, 1, 2), (True, "a", 2), (True, 1, float("nan")), (False, 1, True)):
        try:
            m.if_else_number(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    assert m.SYIfElseNumber.RETURN_TYPES == ("FLOAT", "INT")
    return 9
