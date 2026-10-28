import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_percent_of as m


def run():
    assert m.percent_calc("percent_of", 10, 200)[0] == 20
    assert m.percent_calc("percent_of", 0, 200)[0] == 0
    assert m.percent_calc("percent_of", 50, 3)[0] == 1.5
    assert m.percent_calc("what_percent", 50, 200)[0] == 25
    assert m.percent_calc("what_percent", 300, 100)[0] == 300
    assert m.percent_calc("what_percent", 0, 5)[0] == 0
    assert m.percent_calc("change_by_percent", 200, 10)[0] == 220
    assert m.percent_calc("change_by_percent", 200, -50)[0] == 100
    assert m.percent_calc("change_by_percent", 200, 0)[0] == 200
    assert isinstance(m.percent_calc("percent_of", 1, 1)[1], str)
    for bad in (("what_percent", 5, 0), ("nonsense", 1, 1)):
        try:
            m.percent_calc(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            pass
    assert m.SYPercentOf.RETURN_TYPES == ("FLOAT", "STRING")
    return 14  # checks
