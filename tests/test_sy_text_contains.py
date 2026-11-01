import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_contains as m


def run():
    n = 0
    assert m.text_contains("A Red Cat", "red cat") is True; n += 1
    assert m.text_contains("A Red Cat", "red cat", True) is False; n += 1
    assert m.text_contains("A Red Cat", "Red", True) is True; n += 1
    assert m.text_contains("abc", "xyz") is False; n += 1
    for bad in (("abc", ""), ("abc", 3), (4, "a")):
        try:
            m.text_contains(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            n += 1
    assert m.SYTextContains().run("Hello", "ell")[:2] == (True, "Hello"); n += 1
    assert m.SYTextContains.RETURN_TYPES == ("BOOLEAN", "STRING", "STRING"); n += 1
    return n + _extra()


def _extra():
    n = 0
    assert m.text_contains("concatenate", "cat") is True; n += 1
    assert m.text_contains("concatenate", "cat", False, True) is False; n += 1
    assert m.text_contains("a cat, dog", "cat", False, True) is True; n += 1
    assert m.text_contains("a cat.", "CAT", True, True) is False; n += 1
    assert m.text_contains("red car", "blue\nred", False, False, "any of the lines") is True; n += 1
    assert m.text_contains("red car", "blue\nred", False, False, "all of the lines") is False; n += 1
    assert m.text_contains("red car", "car\nred", False, False, "all of the lines") is True; n += 1
    assert m.text_contains("x.y", "x.y", False, True) is True; n += 1
    assert m.text_contains("xzy", "x.y") is False; n += 1
    for bad in (("a", "\n \n", False, False, "any of the lines"), ("a", "b", False, False, "nope")):
        try:
            m.text_contains(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            n += 1
    f, hit, miss = m.text_contains_info("red car", "red\nblue\ncar", False, False, "any of the lines")
    assert f and hit == ["red", "car"] and miss == ["blue"]; n += 1
    assert m.contains_info(f, hit, miss) == "Found 2 of 3: red, car; missing: blue"; n += 1
    assert m.contains_info(True, ["cat"], []) == "Found 'cat'" and m.contains_info(False, [], ["cat"]) == "Not found: 'cat'"; n += 1
    out = m.SYTextContains().run("A Red Cat", "red\ncat", False, True, "all of the lines")
    assert out == (True, "A Red Cat", "Found 2 of 2: red, cat"); n += 1
    assert m.SYTextContains.RETURN_NAMES[-1] == "info"; n += 1
    return n
