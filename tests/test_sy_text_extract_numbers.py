import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_extract_numbers as m


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    raise SystemExit("expected ValueError")


def run():
    n = 0
    f = m.find_numbers
    assert f("I have 3 apples and 12 pears") == [3, 12]; n += 1
    assert f("Total 1,234.5 EUR") == [1234.5]; n += 1
    assert f("Total 1,234.5 EUR", thousands="ignore") == [1, 234.5]; n += 1
    assert f("1,23 and 1,2345") == [1, 23, 1, 2345]; n += 1
    assert f("temp -7 and +5") == [-7, 5]; n += 1
    assert f("temp -7", allow_negative=False) == [7]; n += 1
    assert f("range 5 - 3") == [5, 3]; n += 1
    assert f("2026-01-31") == [2026, 1, 31]; n += 1
    assert f(".5 and 3.") == [0.5, 3]; n += 1
    assert f("1e3") == [1, 3]; n += 1
    assert f("abc123def4") == [123, 4]; n += 1
    assert f("-.5") == [-0.5]; n += 1
    # kinds
    assert f("1 2.5 3", "whole numbers only") == [1, 3]; n += 1
    assert f("1 2.5 3", "decimals only") == [2.5]; n += 1
    # pick
    assert m.pick_numbers([3, 9, 1], "first") == [3]; n += 1
    assert m.pick_numbers([3, 9, 1], "last") == [1]; n += 1
    assert m.pick_numbers([3, 9, 1], "largest") == [9]; n += 1
    assert m.pick_numbers([3, 9, 1], "smallest") == [1]; n += 1
    assert m.pick_numbers([], "largest") == []; n += 1
    # edge: nothing, empty, one, big
    assert m.extract("no digits here", "all numbers", True, "ignore", "all", ", ") == ("", 0, 0.0, 0.0); n += 1
    assert m.extract("", "all numbers", True, "ignore", "all", ", ") == ("", 0, 0.0, 0.0); n += 1
    assert m.extract("7", "all numbers", True, "ignore", "all", ", ") == ("7", 1, 7.0, 7.0); n += 1
    assert m.extract("a 1 b 2.5 c -3", "all numbers", True, "ignore", "all", " | ") == ("1 | 2.5 | -3", 3, 0.5, 1.0); n += 1
    assert m.extract("1,000,000,000,000", "all numbers", True, m.THOUSANDS[1], "all", ",")[2] == 1e12; n += 1
    assert m.extract("4 8 2", "all numbers", True, "ignore", "largest", ",") == ("8", 1, 8.0, 8.0); n += 1
    # refusals
    assert "kind" in _raises(m.find_numbers, "1", "weird"); n += 1
    assert "thousands" in _raises(m.find_numbers, "1", "all numbers", True, "dots"); n += 1
    assert "pick" in _raises(m.pick_numbers, [1], "middle"); n += 1
    assert "text" in _raises(m.find_numbers, 5); n += 1
    node = m.SYTextExtractNumbers()
    assert node.run("a1 b22", "all numbers", True, "ignore", "all", "+") == ("1+22", 2, 23.0, 1.0); n += 1
    assert m.SYTextExtractNumbers.RETURN_TYPES == ("STRING", "INT", "FLOAT", "FLOAT"); n += 1
    return n
