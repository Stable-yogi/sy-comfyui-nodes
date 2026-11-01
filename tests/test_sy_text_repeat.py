import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_repeat as m


def run():
    assert m.repeat_text("a", 3, ",", False) == "a,a,a"
    assert m.repeat_text("a", 1, ",", False) == "a"
    assert m.repeat_text("a", 2, "", False) == "aa"
    assert m.repeat_text("x", 3, " | ", True) == "1. x | 2. x | 3. x"
    assert m.repeat_text("", 3, "-", False) == "--"
    assert m.repeat_text("a", 200, "", False) == "a" * 200
    assert len(m.repeat_text("ab", 10, "\n", False)) == 29
    for bad in (("a", 0, "", False), ("a", 201, "", False), ("x" * 5000, 200, ",", False)):
        try:
            m.repeat_text(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            pass
    assert m.SYTextRepeat.RETURN_TYPES == ("STRING", "STRING")
    return 11 + _extra()


def _extra():
    n = 0
    assert m.repeat_text("x", 3, " | ", True, 0) == "0. x | 1. x | 2. x"; n += 1
    assert m.repeat_text("x", 2, ",", True, 10) == "10. x,11. x"; n += 1
    assert m.repeat_text("x", 2, ",", False, 10) == "x,x"; n += 1
    assert m.repeat_info("ab", 3, "ab,ab,ab") == "3 copies of 2 character(s), 8 characters in all, about 2 tokens"; n += 1
    assert m.repeat_info("a", 1, "a").startswith("1 copy of 1"); n += 1
    assert "WARNING" in m.repeat_info("", 2, ","); n += 1
    out = m.SYTextRepeat().run("x", 2, "-", True, 5)
    assert out[0] == "5. x-6. x" and out[1].startswith("2 copies"); n += 1
    assert m.SYTextRepeat.RETURN_NAMES == ("text", "info"); n += 1
    return n
