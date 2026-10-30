import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_number_series as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    assert m.number_series(0.0, 1.0, 5) == [0.0, 0.25, 0.5, 0.75, 1.0]; n += 1
    assert m.number_series(0.0, 10.0, 2) == [0.0, 10.0]; n += 1
    assert m.number_series(5.0, 5.0, 3) == [5.0, 5.0, 5.0]; n += 1
    assert m.number_series(1.0, -1.0, 3) == [1.0, 0.0, -1.0]; n += 1
    assert len(m.number_series(0.0, 1.0, 1000)) == 1000; n += 1
    assert m.number_series(0.0, 0.3, 4)[-1] == 0.3; n += 1
    assert m.format_series([0.0, 0.25, 0.5, 0.75, 1.0], 3) == "0, 0.25, 0.5, 0.75, 1"; n += 1
    assert m.format_series([1.0 / 3.0], 3) == "0.333"; n += 1
    assert m.format_series([1.0 / 3.0], 0) == "0"; n += 1
    assert m.format_series([2.5, 12.0], 0) in ("2, 12", "3, 12"); n += 1
    assert m.format_series([-0.0], 3) == "0"; n += 1
    assert m.format_series([-0.0001], 3) == "0"; n += 1
    assert m.format_series([-1.5, 1.5], 1) == "-1.5, 1.5"; n += 1
    assert m.format_series([100.0], 2) == "100"; n += 1
    assert m.format_series([0.123456789], 8) == "0.12345679"; n += 1
    assert m.format_series([], 3) == ""; n += 1
    msg = raises(m.number_series, 0.0, 1.0, 1)
    assert msg and "count" in msg; n += 1
    assert raises(m.number_series, 0.0, 1.0, 1001); n += 1
    msg = raises(m.format_series, [1.0], 9)
    assert msg and "decimals" in msg; n += 1
    assert raises(m.format_series, [1.0], -1); n += 1
    assert m.SYNumberSeries().run(0.0, 1.0, 5, 3) == ("0, 0.25, 0.5, 0.75, 1", 5); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYNumberSeries"] == "Number Series SY"; n += 1
    return n
