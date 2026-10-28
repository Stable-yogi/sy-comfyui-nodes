import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_number_wrap as m


def run():
    assert m.wrap_number(1.25, 0, 1, "wrap")[0] == 0.25
    assert m.wrap_number(-0.25, 0, 1, "wrap")[0] == 0.75
    assert m.wrap_number(5, 0, 10, "wrap")[0] == 5
    assert m.wrap_number(1.25, 0, 1, "ping_pong")[0] == 0.75
    assert m.wrap_number(2.25, 0, 1, "ping_pong")[0] == 0.25
    assert m.wrap_number(-0.25, 0, 1, "ping_pong")[0] == 0.25
    assert m.wrap_number(9, 0, 1, "clamp")[0] == 1
    assert m.wrap_number(-9, 0, 1, "clamp")[0] == 0
    assert m.wrap_number(12, 10, 20, "wrap")[0] == 12
    assert isinstance(m.wrap_number(1, 0, 2, "clamp")[1], str)
    for bad in ((1, 1, 1, "wrap"), (1, 5, 2, "clamp"), (1, 0, 1, "spin")):
        try:
            m.wrap_number(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            pass
    assert m.SYNumberWrap.RETURN_TYPES == ("FLOAT", "STRING")
    return 14  # checks
