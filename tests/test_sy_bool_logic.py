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
    assert m.SYBoolLogic().run(True, False, "or")[0] is True
    for bad in ((1, True, "and"), (True, None, "and"), (True, True, "maybe"), ("yes", True, "or")):
        try:
            m.bool_logic(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    # new operations are the opposite of and / or / xor
    for a in (False, True):
        for b in (False, True):
            assert m.bool_logic(a, b, "nand") is (not m.bool_logic(a, b, "and"))
            assert m.bool_logic(a, b, "nor") is (not m.bool_logic(a, b, "or"))
            assert m.bool_logic(a, b, "xnor") is (not m.bool_logic(a, b, "xor"))
            n += 3
    assert m.OPERATIONS[:4] == ("and", "or", "xor", "not")            # old choices keep their place
    assert m.SYBoolLogic().run(True, False, "or") == (True, "yes or no -> yes")
    assert m.SYBoolLogic().run(True, True, "not") == (False, "not yes -> no")
    assert m.SYBoolLogic.RETURN_TYPES == ("BOOLEAN", "STRING")
    return n + 9
