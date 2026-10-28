import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_layout_boxes_preview as m
from _sy_layout import COLOUR_RGB, box_rect


def bad(text):
    try:
        m.plan_boxes(text, 100, 100)
    except ValueError as e:
        return str(e)
    raise SystemExit("must raise: %r" % (text,))


def run():
    b = {"x": 10, "y": 20, "w": 30, "h": 40}
    assert box_rect(b, 100, 100) == (10, 20, 40, 60)
    assert box_rect({"x": 90, "y": 90, "w": 30, "h": 30}, 100, 100) == (90, 90, 100, 100)     # clipped to canvas
    assert box_rect({"x": -10, "y": -10, "w": 30, "h": 30}, 100, 100) == (0, 0, 20, 20)
    assert box_rect({"x": 100, "y": 0, "w": 10, "h": 10}, 100, 100) is None                    # fully outside
    assert box_rect({"x": 0, "y": 0, "w": 0, "h": 10}, 100, 100) is None
    assert box_rect({"x": 0, "y": 0, "w": 100, "h": 100}, 100, 100) == (0, 0, 100, 100)
    plan = m.plan_boxes(json.dumps([dict(b, label="hi", colour="blue")]), 100, 100)
    assert plan == [((10, 20, 40, 60), COLOUR_RGB["blue"], "hi")]
    assert m.plan_boxes(json.dumps([dict(b, color="pink")]), 100, 100)[0][1] == COLOUR_RGB["pink"]   # US spelling
    assert m.plan_boxes(json.dumps([b]), 100, 100)[0][1] == COLOUR_RGB["red"]                       # default colour
    assert m.plan_boxes(json.dumps([dict(b, colour="mauve")]), 100, 100)[0][1] == COLOUR_RGB["red"]
    assert m.plan_boxes(json.dumps([dict(b, x=500)]), 100, 100) == []                               # outside: skipped
    assert m.plan_boxes(json.dumps(b), 100, 100)[0][0] == (10, 20, 40, 60)                          # single object
    assert m.plan_boxes(json.dumps([dict(b, label=5)]), 100, 100)[0][2] == ""
    assert "box 1 needs numbers" in bad('[{"x": "a", "y": 0, "w": 5, "h": 5}]')
    assert "box 2 needs numbers" in bad('[{"x": 0, "y": 0, "w": 5, "h": 5}, {"x": 0}]')
    assert "not valid JSON" in bad("{oops")
    assert "empty" in bad("")
    assert "not an object" in bad("[3]")
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYLayoutBoxesPreview"] == "Layout Boxes Preview SY"
    assert m.SYLayoutBoxesPreview.RETURN_TYPES == ("IMAGE",)
    return 20
