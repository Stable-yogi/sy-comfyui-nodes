import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_dehaze as m


def _refuses(fn, word, *args):
    try:
        fn(*args)
    except ValueError as e:
        assert word in str(e), str(e)
        return 1
    raise SystemExit("expected ValueError")


def run():
    n = 0
    # normal: mean of the top 0.1 percent (1000 values -> the single largest)
    vals = [i / 1000.0 for i in range(1000)]
    assert abs(m.estimate_airlight(vals) - 0.999) < 1e-9
    # 4000 values -> top 4
    vals = [0.2] * 3996 + [0.8, 0.9, 1.0, 0.7]
    assert abs(m.estimate_airlight(vals) - 0.85) < 1e-9
    n += 2
    # edge: few values use the single largest; order does not matter; one value works
    assert m.estimate_airlight([0.3, 0.9, 0.1]) == 0.9
    assert m.estimate_airlight([0.5]) == 0.5
    n += 2
    # floor
    assert m.transmission_floor(0.05, 0.1) == 0.1 and m.transmission_floor(0.7, 0.1) == 0.7
    assert m.transmission_floor(0.0) == 0.1 and m.transmission_floor(1.0, 0.0) == 1.0
    n += 2
    # refusals
    n += _refuses(m.estimate_airlight, "no pixel", [])
    n += _refuses(m.transmission_floor, "floor", 0.5, 1.5)
    d = m.SYDehaze.INPUT_TYPES()["required"]
    assert d["amount"][1]["default"] == 0.5 and d["patch"][1]["default"] == 15
    assert d["sky_protect"][1]["default"] == 0.5 and d["saturation_back"][1]["default"] == 0.3
    n += 1
    return n
