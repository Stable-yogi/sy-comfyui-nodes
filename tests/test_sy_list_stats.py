import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_list_stats as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def near(a, b, eps=1e-9):
    return abs(a - b) < eps


def run():
    n = 0
    assert m.parse_numbers("1, 2 3\n4") == [1.0, 2.0, 3.0, 4.0]; n += 1
    assert m.parse_numbers("  -1.5,2e2 ") == [-1.5, 200.0]; n += 1
    assert m.parse_numbers("7") == [7.0]; n += 1
    assert m.parse_numbers("1,,2") == [1.0, 2.0]; n += 1
    s = m.list_stats([3.0, 1.0, 2.0])
    assert s["count"] == 3 and s["sum"] == 6.0 and s["mean"] == 2.0 and s["median"] == 2.0; n += 1
    assert s["min"] == 1.0 and s["max"] == 3.0; n += 1
    assert m.list_stats([1.0, 2.0, 3.0, 10.0])["median"] == 2.5; n += 1
    s = m.list_stats([5.0])
    assert s["count"] == 1 and s["median"] == 5.0 and s["mean"] == 5.0; n += 1
    s = m.list_stats([-2.0, 2.0])
    assert s["sum"] == 0.0 and s["min"] == -2.0; n += 1
    assert m.list_stats([1.0, 2.0])["summary"] == "count=2 sum=3.000 mean=1.500 median=1.500 min=1.000 max=2.000"; n += 1
    assert "\n" not in m.list_stats([1.0, 2.0])["summary"]; n += 1
    assert near(m.list_stats([0.1] * 10)["sum"], 1.0); n += 1
    msg = raises(m.parse_numbers, "")
    assert msg and "numbers is empty" in msg; n += 1
    msg = raises(m.parse_numbers, " , \n ")
    assert msg and "numbers is empty" in msg; n += 1
    msg = raises(m.parse_numbers, "1, two, 3")
    assert msg and "two" in msg; n += 1
    msg = raises(m.parse_numbers, "1 nan")
    assert msg and "nan" in msg; n += 1
    assert raises(m.parse_numbers, "inf"); n += 1
    msg = raises(m.list_stats, [])
    assert msg and "numbers is empty" in msg; n += 1
    r = m.SYListStats().run("4 8")
    assert r[0] == 2 and r[2] == 6.0 and len(r) == 7; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYListStats"] == "List Stats SY"; n += 1
    assert m.SYListStats.CATEGORY == "SY/Values"; n += 1
    return n
