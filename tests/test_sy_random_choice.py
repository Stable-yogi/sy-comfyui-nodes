import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_random_choice as m


def run():
    text = "red\n\n  green  \nblue\n"
    a = m.pick_line(text, 7)
    assert a == m.pick_line(text, 7)
    assert a[0] in ("red", "green", "blue") and 0 <= a[1] < 3
    assert ["red", "green", "blue"][a[1]] == a[0]
    seen = {m.pick_line(text, s)[0] for s in range(60)}
    assert seen == {"red", "green", "blue"}
    assert m.pick_line("only", 123) == ("only", 0)
    for bad in ("", "  \n \n"):
        try:
            m.pick_line(bad, 1)
            raise SystemExit("empty must raise")
        except ValueError:
            pass
    assert m.SYRandomChoice().run("x\ny", 3)[0] in ("x", "y")
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYRandomChoice"] == "Random Choice SY"
    return 9
