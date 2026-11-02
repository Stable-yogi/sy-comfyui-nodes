import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_cumulative_sum as m


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected ValueError")


def run():
    n = 0
    assert m.parse_numbers("1, 2 3\n4;5.5") == [1.0, 2.0, 3.0, 4.0, 5.5]; n += 1
    assert m.parse_numbers("  ") == []; n += 1
    assert m.parse_numbers("-1,+2") == [-1.0, 2.0]; n += 1
    v = [3.0, 1.0, 4.0, 1.0, 5.0]
    assert m.running(v, "running total") == [3.0, 4.0, 8.0, 9.0, 14.0]; n += 1
    assert m.running(v, "running average") == [3.0, 2.0, 8 / 3, 2.25, 2.8]; n += 1
    assert m.running(v, "running maximum") == [3.0, 3.0, 4.0, 4.0, 5.0]; n += 1
    assert m.running(v, "running minimum") == [3.0, 1.0, 1.0, 1.0, 1.0]; n += 1
    assert m.running(v, "difference from previous") == [0.0, -2.0, 3.0, -3.0, 4.0]; n += 1
    assert m.running([], "running total") == []; n += 1
    assert m.running([7.0], "difference from previous") == [0.0]; n += 1
    assert m.cumulative("1, 2, 3, 4", "running total", ", ", 2) == ("1, 3, 6, 10", 10.0, 4); n += 1
    assert m.cumulative("0.1 0.2 0.3", "running total", " | ", 2) == ("0.1 | 0.3 | 0.6", 0.6000000000000001, 3); n += 1
    assert m.cumulative("1\n2", "running average", ",", 1) == ("1,1.5", 1.5, 2); n += 1
    assert m.cumulative("-5", "running total", ", ", 0) == ("-5", -5.0, 1); n += 1
    assert m.cumulative("", "running total", ", ", 2) == ("", 0.0, 0); n += 1
    big = " ".join(["1"] * 5000)
    r = m.cumulative(big, "running total", ",", 0)
    assert r[1] == 5000.0 and r[2] == 5000; n += 1
    assert "not a normal number" in _raises(m.parse_numbers, "1e400"); n += 1
    # refusals
    msg = _raises(m.cumulative, "1, two, 3", "running total", ", ", 2)
    assert "item 2" in msg and "two" in msg; n += 1
    assert "not a normal number" in _raises(m.parse_numbers, "1 nan"); n += 1
    assert "not a normal number" in _raises(m.parse_numbers, "inf"); n += 1
    assert "mode" in _raises(m.cumulative, "1", "median", ", ", 2); n += 1
    assert "mode" in _raises(m.cumulative, "", "median", ", ", 2); n += 1
    assert "decimals" in _raises(m.cumulative, "1", "running total", ", ", 11); n += 1
    node = m.SYCumulativeSum()
    assert node.run("2 2 2", "running total", "-", 0) == ("2-4-6", 6.0, 3); n += 1
    return n
