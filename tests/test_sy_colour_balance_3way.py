import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_colour_balance_3way as m
import _sy_ae_common as ae


def run():
    n = 0
    # weights always add up to 1
    for i in range(0, 101):
        s, mid, h = m.zone_weights(i / 100.0)
        assert abs(s + mid + h - 1.0) < 1e-9 and min(s, mid, h) >= 0.0
        n += 1
    # edge: black is all shadow, mid grey all mid, white all high
    assert m.zone_weights(0.0) == (1.0, 0.0, 0.0)
    assert m.zone_weights(0.5) == (0.0, 1.0, 0.0)
    assert m.zone_weights(1.0) == (0.0, 0.0, 1.0)
    n += 3
    # smooth: neighbouring values do not jump
    prev = m.zone_weights(0.0)
    for i in range(1, 1001):
        cur = m.zone_weights(i / 1000.0)
        assert max(abs(a - b) for a, b in zip(prev, cur)) < 0.02
        prev = cur
    n += 1
    # refusal
    try:
        m.zone_weights(1.5)
        raise SystemExit("expected ValueError")
    except ValueError as e:
        assert "luma" in str(e)
    n += 1
    # nine sliders plus strength, all with tooltips
    req = m.SYColourBalance3Way.INPUT_TYPES()["required"]
    names = [k for k in req if k != "image"]
    assert len(names) == 10 and names[-1] == "strength"
    assert req["strength"][1]["default"] == 1.0
    assert all(req[k][1]["default"] == 0.0 for k in names[:9])
    n += 3
    try:
        ae.check_shape((2, 3, 3, 3, 3))
        raise SystemExit("expected ValueError")
    except ValueError:
        pass
    n += 1
    return n
