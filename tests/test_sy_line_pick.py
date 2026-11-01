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
    assert m.SYLinePick.RETURN_TYPES == ("STRING", "INT", "STRING")
    assert m.line_pick("a\nb\nc", 3, True, "wrap around") == ("a", 3)
    assert m.line_pick("a\nb\nc", 7, True, "wrap around") == ("b", 3)
    assert m.line_pick("a\nb\nc", -4, True, "wrap around") == ("c", 3)
    assert m.line_pick("a\nb\nc", 9, True, "clamp to ends") == ("c", 3)
    assert m.line_pick("a\nb\nc", -9, True, "clamp to ends") == ("a", 3)
    assert m.line_pick("a\nb\nc", 1, True, "wrap around") == ("b", 3)
    assert m.line_pick("  a  \nb", 0, True, "error", True) == ("a", 2)
    assert m.line_pick("  a  \nb", 0, True, "error", False) == ("  a  ", 2)
    assert m.line_pick_ex("a\nb", 5, True, "wrap around") == ("b", 2, 1, "wrapped")
    assert m.line_pick_ex("a\nb", 5, True, "clamp to ends") == ("b", 2, 1, "clamped")
    assert m.line_pick_ex("a\nb", -1, True) == ("b", 2, 1, "")
    for bad in (("a\nb", 2, True, "error"), ("", 0, True, "wrap around"), ("\n", 0, True, "clamp to ends"), ("a", 0, True, "sideways")):
        try:
            m.line_pick(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            pass
    assert m.SYLinePick().run("a\nb\nc", 1, True) == ("b", 3, "Picked line 2 of 3.")
    assert m.SYLinePick().run("a\nb\nc", 4, True, "wrap around") == ("b", 3, "Picked line 2 of 3 (index 4 wrapped round).")
    assert m.SYLinePick().run("a\nb\nc", 4, True, "clamp to ends")[2] == "Picked line 3 of 3 (index 4 was past the end)."
    assert m.SYLinePick.RETURN_NAMES == ("line", "total_lines", "info")
    return 28  # checks
