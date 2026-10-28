import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_number_compare as m


def run():
    c = m.number_compare
    table = {
        "==": (False, True, False), "!=": (True, False, True),
        "<": (True, False, False), "<=": (True, True, False),
        ">": (False, False, True), ">=": (False, True, True),
    }
    n = 0
    for op, (lt, eq, gt) in table.items():
        assert c(1, 2, op) is lt
        assert c(2, 2, op) is eq
        assert c(3, 2, op) is gt
        n += 3
    assert m.SYNumberCompare().run(1.0, "<", 2.0) == (True,)
    for bad in ((1, 2, "="), (1, 2, "<>"), (float("nan"), 1, "=="), ("a", 1, "=="), (1, True, "==")):
        try:
            c(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    assert m.SYNumberCompare.RETURN_TYPES == ("BOOLEAN",)
    return n + 7
