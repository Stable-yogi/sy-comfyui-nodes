import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_cycle_pick as m


def run():
    text = "red\n\ngreen\n  \nblue\n"
    assert m.parse_items(text) == ["red", "green", "blue"]
    assert m.cycle_pick(text, 0) == ("red", 0, 3)
    assert m.cycle_pick(text, 2) == ("blue", 2, 3)
    assert m.cycle_pick(text, 3) == ("red", 0, 3)
    assert m.cycle_pick(text, 7) == ("green", 1, 3)
    assert m.cycle_pick(text, -1) == ("blue", 2, 3)
    assert m.cycle_pick("only", 99) == ("only", 0, 1)
    assert m.cycle_pick("a\r\nb", 1) == ("b", 1, 2)
    for bad in ("", "   \n\n  "):
        try:
            m.cycle_pick(bad, 0)
            raise SystemExit("empty list must raise")
        except ValueError:
            pass
    assert m.SYCyclePick.RETURN_TYPES == ("STRING", "INT", "INT")
    return 11  # checks
