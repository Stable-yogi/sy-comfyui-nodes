import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_table_pick as m


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected ValueError")


def run():
    n = 0
    t = "name,age,city\nAnn,30,Oslo\nBob,25,Rome\n"
    rows = m.parse_table(t)
    assert rows == [["name", "age", "city"], ["Ann", "30", "Oslo"], ["Bob", "25", "Rome"]]; n += 1
    assert m.pick_cell(rows, 0, "age") == ("30", True, 2); n += 1
    assert m.pick_cell(rows, 1, " CITY ") == ("Rome", True, 2); n += 1
    assert m.pick_cell(rows, 1, "1") == ("Bob", True, 2); n += 1
    # quoted cells and doubled quotes
    q = m.parse_table('a,b\n"x, y","say ""hi"""\n')
    assert q[1] == ["x, y", 'say "hi"']; n += 1
    # delimiters
    assert m.detect_delimiter("a\tb\tc,d") == "\t"; n += 1
    assert m.detect_delimiter("a;b;c") == ";"; n += 1
    assert m.detect_delimiter("a|b") == "|"; n += 1
    assert m.detect_delimiter("abc") == ","; n += 1
    assert m.parse_table("a|b\n1|2", "auto") == [["a", "b"], ["1", "2"]]; n += 1
    assert m.parse_table("a,b|c", "pipe") == [["a,b", "c"]]; n += 1
    # windows line ends and blank lines
    assert m.parse_table("a,b\r\n\r\n1,2\r\n") == [["a", "b"], ["1", "2"]]; n += 1
    # edge: empty, one row, header only, last row
    assert m.parse_table("") == []; n += 1
    assert m.pick_cell([], 0, "1", True, "dflt") == ("dflt", False, 0); n += 1
    assert m.pick_cell([["h"]], 0, "h", True, "d") == ("d", False, 0); n += 1
    assert m.pick_cell([["h"], ["v"]], 0, "h") == ("v", True, 1); n += 1
    assert m.pick_cell(rows, 100000, "name", True, "none") == ("none", False, 2); n += 1
    assert m.pick_cell(rows, 1, "3") == ("Rome", True, 2); n += 1
    assert m.pick_cell(rows, 0, "9", True, "z") == ("z", False, 2); n += 1
    # no header: first row is data
    assert m.pick_cell(rows, 0, "1", False) == ("name", True, 3); n += 1
    # header name wins over a number
    assert m.pick_cell([["2", "x"], ["a", "b"]], 0, "2") == ("a", True, 1); n += 1
    # refusals
    assert "no column named" in _raises(m.pick_cell, rows, 0, "zip"); n += 1
    assert "has_header is off" in _raises(m.pick_cell, rows, 0, "name", False); n += 1
    assert "start at 1" in _raises(m.pick_cell, rows, 0, "0"); n += 1
    assert "empty" in _raises(m.pick_cell, rows, 0, "  "); n += 1
    assert "never closed" in _raises(m.parse_table, 'a,"b'); n += 1
    assert "delimiter" in _raises(m.parse_table, "a", "dot"); n += 1
    assert "0 or more" in _raises(m.pick_cell, rows, -1, "name"); n += 1
    node = m.SYTablePick()
    assert node.run(t, 1, "name", True, "auto", "") == ("Bob", True, 2); n += 1
    assert m.SYTablePick.RETURN_TYPES == ("STRING", "BOOLEAN", "INT"); n += 1
    return n
