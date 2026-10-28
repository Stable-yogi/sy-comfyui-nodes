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
    assert m.SYTextRepeat.RETURN_TYPES == ("STRING",)
    return 11  # checks
