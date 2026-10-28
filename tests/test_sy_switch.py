import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_switch as m


def run():
    assert m.pick(True, 1, 2) == 1
    assert m.pick(False, 1, 2) == 2
    n = m.SYSwitch()
    assert n.run(True, "a", "b") == ("a",)
    assert n.run(False, "a", "b") == ("b",)
    assert n.check_lazy_status(True) == ["a"]
    assert n.check_lazy_status(False) == ["b"]
    assert not (m.ANY != "IMAGE")
    return 6
