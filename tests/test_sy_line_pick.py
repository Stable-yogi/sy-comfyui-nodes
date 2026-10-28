import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_line_pick as m


def run():
    text = "one\n\ntwo\nthree"
    assert m.line_pick(text, 0, True) == ("one", 3)
    assert m.line_pick(text, 1, True) == ("two", 3)
    assert m.line_pick(text, 1, False) == ("", 4)
    assert m.line_pick(text, -1, True) == ("three", 3)
    assert m.line_pick(text, -3, True) == ("one", 3)
    assert m.line_pick(text, 3, False) == ("three", 4)
    assert m.line_pick("solo", 0, True) == ("solo", 1)
    assert m.line_pick("a\r\nb", 1, True) == ("b", 2)
    for bad in (("a\nb", 2, True), ("a\nb", -3, True), ("", 0, True), ("\n\n", 0, True)):
        try:
            m.line_pick(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            pass
    assert m.SYLinePick.RETURN_TYPES == ("STRING", "INT")
    return 13  # checks
