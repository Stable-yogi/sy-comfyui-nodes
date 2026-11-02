import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_oil_paint as m
import _sy_ae_common as ae


def run():
    n = 0
    # normal: smallest wins
    assert m.pick_lowest([0.3, 0.1, 0.2, 0.4]) == 1
    assert m.pick_lowest([0.4, 0.3, 0.2, 0.1]) == 3
    n += 2
    # edge: ties go to the first, single item, zero values
    assert m.pick_lowest([0.2, 0.2, 0.2, 0.2]) == 0
    assert m.pick_lowest([5]) == 0
    assert m.pick_lowest([0.0, 0.0, 1e-9, 0.0]) == 0
    n += 3
    # works with any iterable
    assert m.pick_lowest(iter((3, 2, 1))) == 2
    n += 1
    # refusals
    try:
        m.pick_lowest([])
        raise SystemExit("expected ValueError")
    except ValueError as e:
        assert "variance" in str(e)
    n += 1
    for shape in ((0, 4, 4, 3), (4,), (1, 2, 3, 4, 5)):
        try:
            ae.check_shape(shape)
            raise SystemExit("expected ValueError")
        except ValueError:
            pass
    n += 3
    d = m.SYOilPaint.INPUT_TYPES()["required"]["radius"][1]
    assert d["default"] == 4 and d["min"] == 1 and d["max"] == 10
    n += 1
    return n
