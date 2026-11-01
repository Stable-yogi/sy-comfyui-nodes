import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_if_else_number as m


def run():
    assert m.if_else_number(True, 1.5, 9) == (1.5, 2)
    assert m.if_else_number(False, 1.5, 9) == (9.0, 9)
    assert m.if_else_number(False, 0, -2.5) == (-2.5, -3)
    assert m.SYIfElseNumber().run(True, 3.0, 4.0)[:2] == (3.0, 3)
    for bad in ((1, 1, 2), (True, "a", 2), (True, 1, float("nan")), (False, 1, True)):
        try:
            m.if_else_number(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    # new: rounding choices and info
    assert [m.to_whole(2.5, r) for r in m.ROUNDING] == [3, 2, 3, 2]
    assert [m.to_whole(-2.5, r) for r in m.ROUNDING] == [-3, -3, -2, -2]
    assert [m.to_whole(2.4, r) for r in m.ROUNDING] == [2, 2, 3, 2]
    assert m.if_else_number(True, 2.7, 0, "floor") == (2.7, 2)
    assert m.if_else_number(True, 2.7, 0, "toward zero") == (2.7, 2)
    assert m.if_else_number(True, -2.7, 0, "ceil") == (-2.7, -2)
    assert m.if_else_number(True, 2.5, 0) == (2.5, 3)                 # default rounding is unchanged
    try:
        m.if_else_number(True, 1, 2, "up")
        raise SystemExit("must raise")
    except ValueError as e:
        assert "rounding" in str(e)
    assert m.if_else_info(True, 1.5, 2) == "yes: took if_true = 1.5, whole number 2 (nearest)"
    assert m.if_else_info(False, 9.0, 9) == "no: took if_false = 9"
    assert m.SYIfElseNumber().run(False, 1.0, 5.5, "ceil") == (5.5, 6, "no: took if_false = 5.5, whole number 6 (ceil)")
    assert m.SYIfElseNumber.RETURN_TYPES == ("FLOAT", "INT", "STRING") and len(m.SYIfElseNumber.RETURN_NAMES) == 3
    assert m.SYIfElseNumber.RETURN_NAMES[:2] == ("float", "int")
    return 25
