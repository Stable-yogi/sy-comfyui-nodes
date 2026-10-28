import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_layout_box as m
from _sy_layout import COLOUR_NAMES, MAX_LABEL


def raises(*args):
    try:
        m.layout_box_text(*args)
    except ValueError:
        return True
    return False


def run():
    data = json.loads(m.layout_box_text(10, 20, 300, 400, "  sign ", "green"))
    assert data == [{"x": 10, "y": 20, "w": 300, "h": 400, "label": "sign", "colour": "green"}]
    assert json.loads(m.layout_box_text(0, 0, 1, 1, "", "red"))[0]["label"] == ""
    assert json.loads(m.layout_box_text(0, 0, 1, 1, None, "red"))[0]["label"] == ""
    assert json.loads(m.layout_box_text(0, 0, 1, 1, "x" * MAX_LABEL, "red"))[0]["label"] == "x" * MAX_LABEL
    assert isinstance(m.layout_box_text(1, 2, 3, 4, "a", "blue"), str)
    for name in COLOUR_NAMES:
        assert json.loads(m.layout_box_text(0, 0, 5, 5, "c", name))[0]["colour"] == name
    assert raises(0, 0, 0, 5, "a", "red")            # no width
    assert raises(0, 0, 5, 0, "a", "red")            # no height
    assert raises(-1, 0, 5, 5, "a", "red")
    assert raises(0, -1, 5, 5, "a", "red")
    assert raises("1", 0, 5, 5, "a", "red")
    assert raises(0, 0, 5, 5, "x" * (MAX_LABEL + 1), "red")
    assert raises(0, 0, 5, 5, "a", "mauve")
    assert m.SYLayoutBox().run(1, 2, 3, 4, "q", "cyan")[0] == m.layout_box_text(1, 2, 3, 4, "q", "cyan")
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYLayoutBox"] == "Layout Box SY"
    return 16 + len(COLOUR_NAMES)
