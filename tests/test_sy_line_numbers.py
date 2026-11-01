import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_line_numbers as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    assert m.number_lines(["a", "b"], 1, ". ", False, False) == (["1. a", "2. b"], 2); n += 1
    assert m.number_lines([], 1, ". ", False, False) == ([], 0); n += 1
    assert m.number_lines([""], 1, ". ", False, False) == (["1. "], 1); n += 1
    assert m.number_lines(["a", "b", "c"], 10, ")", False, False) == (["10)a", "11)b", "12)c"], 3); n += 1
    out, c = m.number_lines(["a"] * 10, 1, " ", True, False)
    assert out[0] == "01 a" and out[9] == "10 a" and c == 10; n += 1
    out, c = m.number_lines(["a"] * 3, 1, " ", True, False)
    assert out[0] == "1 a"; n += 1
    out, c = m.number_lines(["a", "", "b", "  ", "c"], 1, ". ", False, True)
    assert out == ["1. a", "", "2. b", "  ", "3. c"] and c == 3; n += 1
    out, c = m.number_lines(["", ""], 1, ". ", False, True)
    assert out == ["", ""] and c == 0; n += 1
    out, c = m.number_lines(["a", "", "b"], 1, ". ", False, False)
    assert out[1] == "2. " and c == 3; n += 1
    out, c = m.number_lines(["a", "b"], 0, ".", False, False)
    assert out == ["0.a", "1.b"]; n += 1
    out, c = m.number_lines(["a", "b", "c"], -1, ".", False, False)
    assert out == ["-1.a", "0.b", "1.c"]; n += 1
    out, c = m.number_lines(["a", "b"], 99, ".", True, False)
    assert out == ["099.a", "100.b"]; n += 1
    out, c = m.number_lines(["a", "b"], 1, "", False, False)
    assert out == ["1a", "2b"]; n += 1
    msg = raises(m.number_lines, ["a"], 2000000, ". ", False, False)
    assert msg and "start" in msg; n += 1
    assert raises(m.number_lines, ["a"], -1000001, ". ", False, False); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYLineNumbers"] == "Line Numbers SY"; n += 1
    assert m.SYLineNumbers.CATEGORY == "SY/Text"; n += 1
    assert m.SYLineNumbers().run("a\r\nb\n\nc", 1, ". ", False, True) == ("1. a\n2. b\n\n3. c", 3, "Numbered 3 lines, starting at 1."); n += 1
    assert m.strip_numbers(["1. a", "2. b"], ". ") == (["a", "b"], 2); n += 1
    assert m.strip_numbers(["10) a", "b", "3 c", "-1. d"], ". ") == (["a", "b", "c", "d"], 3); n += 1
    assert m.strip_numbers(["01 a", "02 b"], " ") == (["a", "b"], 2); n += 1
    assert m.strip_numbers(["1.a"], ".") == (["a"], 1); n += 1
    assert m.strip_numbers(["2024 was good"], ". ") == (["was good"], 1); n += 1
    assert m.strip_numbers(["no number", ""], ". ") == (["no number", ""], 0); n += 1
    assert m.SYLineNumbers().run("1. a\n2. b\nc", 1, ". ", False, False, "remove numbers") == ("a\nb\nc", 2, "Removed the number from 2 of 3 lines."); n += 1
    assert m.SYLineNumbers().run("", 1, ". ", False, True)[2] == "Numbered 0 lines: nothing to number."; n += 1
    assert m.SYLineNumbers().run("a", 5, ". ", False, False)[2] == "Numbered 1 line, starting at 5."; n += 1
    assert raises(lambda: m.SYLineNumbers().run("a", 1, ". ", False, False, "flip")); n += 1
    assert m.SYLineNumbers.RETURN_NAMES == ("text", "count", "info"); n += 1
    return n
