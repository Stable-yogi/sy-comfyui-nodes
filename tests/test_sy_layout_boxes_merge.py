import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_layout_boxes_merge as m
from sy_layout_box import layout_box_text
from _sy_layout import MAX_BOXES


def bad(texts):
    try:
        m.merge_boxes(texts)
    except ValueError as e:
        return str(e)
    raise SystemExit("must raise: %r" % (texts,))


def run():
    a = layout_box_text(0, 0, 10, 10, "a", "red")
    b = layout_box_text(10, 0, 10, 10, "b", "blue")
    c = layout_box_text(20, 0, 10, 10, "c", "green")
    d = layout_box_text(30, 0, 10, 10, "d", "pink")
    out = json.loads(m.merge_boxes([a, b, c, d]))
    assert [x["label"] for x in out] == ["a", "b", "c", "d"]
    assert [x["label"] for x in json.loads(m.merge_boxes([d, "", a, ""]))] == ["d", "a"]
    assert [x["label"] for x in json.loads(m.merge_boxes([None, "  ", b]))] == ["b"]
    assert json.loads(m.merge_boxes([a])) == json.loads(a)
    # an already merged list can be merged again, and a single object is accepted
    ab = m.merge_boxes([a, b])
    assert [x["label"] for x in json.loads(m.merge_boxes([ab, c]))] == ["a", "b", "c"]
    assert json.loads(m.merge_boxes(['{"x": 1, "y": 2, "w": 3, "h": 4}']))[0]["w"] == 3
    assert "all four inputs are empty" in bad(["", "", "", ""])
    assert "all four inputs are empty" in bad([None, None])
    assert "input 2" in bad([a, "{broken"])
    assert "input 1" in bad(["42"])
    assert "input 3" in bad([a, "", "[1]"])
    many = json.dumps([{"x": 0, "y": 0, "w": 1, "h": 1}] * MAX_BOXES)
    assert len(json.loads(m.merge_boxes([many]))) == MAX_BOXES
    assert "most allowed" in bad([many, a])
    assert m.SYLayoutBoxesMerge().run(boxes_1=a, boxes_3=c)[0] == m.merge_boxes([a, "", c, ""])
    assert m.SYLayoutBoxesMerge().run(boxes_2=b)[0] == m.merge_boxes([b])
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYLayoutBoxesMerge"] == "Layout Boxes Merge SY"
    return 17
