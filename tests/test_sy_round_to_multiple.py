import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_round_to_multiple as m


def run():
    r = m.round_to_multiple
    assert r(70, 64) == (64.0, 64)
    assert r(100, 64) == (128.0, 128)
    assert r(96, 64) == (128.0, 128)       # half goes up
    assert r(70, 64, "up") == (128.0, 128)
    assert r(70, 64, "down") == (64.0, 64)
    assert r(64, 64, "up") == (64.0, 64)   # already a multiple stays
    assert r(64, 64, "down") == (64.0, 64)
    assert r(-70, 64) == (-64.0, -64)
    assert r(-70, 64, "down") == (-128.0, -128)
    assert r(-70, 64, "up") == (-64.0, -64)
    assert r(0, 8) == (0.0, 0)
    assert r(0.3, 0.1, "down") == (0.3, 0)
    assert r(1.26, 0.5) == (1.5, 2)
    assert r(7.0, 2.5, "up") == (7.5, 8)
    assert m.SYRoundToMultiple().run(1000, 64, "down") == (960.0, 960)
    for bad in ((1, 0), (1, -4), (1, 2, "sideways"), (float("nan"), 2), ("a", 2), (1, True)):
        try:
            r(*bad)
            raise SystemExit("must raise for %r" % (bad,))
        except ValueError as e:
            assert str(e)
    assert m.SYRoundToMultiple.RETURN_TYPES == ("FLOAT", "INT")
    return 22
