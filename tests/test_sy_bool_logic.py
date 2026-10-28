import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_bool_logic as m


def run():
    t = {
        "and": {(False, False): False, (False, True): False, (True, False): False, (True, True): True},
        "or": {(False, False): False, (False, True): True, (True, False): True, (True, True): True},
        "xor": {(False, False): False, (False, True): True, (True, False): True, (True, True): False},
        "not": {(False, False): True, (False, True): True, (True, False): False, (True, True): False},
    }
    n = 0
    for op, rows in t.items():
        for (a, b), want in rows.items():
            assert m.bool_logic(a, b, op) is want, (op, a, b)
            n += 1
    assert m.SYBoolLogic().run(True, False, "or") == (True,)
    for bad in ((1, True, "and"), (True, None, "and"), (True, True, "nand"), ("yes", True, "or")):
        try:
            m.bool_logic(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    assert m.SYBoolLogic.RETURN_TYPES == ("BOOLEAN",)
    return n + 6
