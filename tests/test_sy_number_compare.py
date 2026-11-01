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
    assert m.SYNumberCompare().run(1.0, "<", 2.0)[:1] == (True,)
    for bad in ((1, 2, "="), (1, 2, "<>"), (float("nan"), 1, "=="), ("a", 1, "=="), (1, True, "==")):
        try:
            c(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    assert m.SYNumberCompare.RETURN_TYPES[:1] == ("BOOLEAN",)
    return n + 7 + _extra(m)


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
    n += ok(m.number_compare(0.1 + 0.2, 0.3, '==') is False)
    n += ok(m.number_compare(0.1 + 0.2, 0.3, '==', 1e-9) is True)
    n += ok(m.number_compare(0.1 + 0.2, 0.3, '!=', 1e-9) is False)
    n += ok(m.number_compare(1.0, 1.00001, '<', 0.001) is False)
    n += ok(m.number_compare(1.0, 1.00001, '<=', 0.001) is True)
    n += ok(m.number_compare(2.0, 1.0, '>', 0.5) is True)
    n += ok(m.number_compare(1.2, 1.0, '>=', 0.5) is True)
    n += ok(rs(m.number_compare, 1, 2, '==', -1) is not None)
    n += ok(m.compare_info(1, 2, '<')[0] == -1)
    n += ok('is yes' in m.compare_info(1, 2, '<')[1])
    n += ok('within' in m.compare_info(1, 2, '<', 0.5)[1])
    n += ok(m.SYNumberCompare().run(1.0, '==', 1.0)[1].endswith('(a minus b = 0)'))
    return n
