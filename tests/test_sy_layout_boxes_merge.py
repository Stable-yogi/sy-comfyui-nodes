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
    # new: eight inputs, drop_duplicates, count and info
    e = layout_box_text(40, 0, 10, 10, "e", "red")
    out = json.loads(m.SYLayoutBoxesMerge().run(boxes_5=e, boxes_8=a)[0])
    assert [x["label"] for x in out] == ["e", "a"]
    assert "all 8 inputs are empty" in bad([""] * 8)
    assert "input 7" in bad([""] * 6 + ["{broken"])
    text, count, info = m.merge_details([a, b, "", c])
    assert count == 3 and info == "Joined 3 boxes from 3 inputs."
    assert m.merge_details([a])[2] == "Joined 1 box from 1 input."
    assert m.merge_details([a, a, b], False)[1] == 3                     # copies kept by default
    text, count, info = m.merge_details([a, a, b], True)
    assert count == 2 and [x["label"] for x in json.loads(text)] == ["a", "b"] and "Dropped 1 exact copy." in info
    assert "Dropped 2 exact copies." in m.merge_details([a, a, a], True)[2]
    near = layout_box_text(0, 0, 10, 11, "a", "red")                     # different size: not a copy
    assert m.merge_details([a, near], True)[1] == 2
    assert 'Same label used twice: "a"' in m.merge_details([a, near])[2]
    assert "Same label" not in m.merge_details([a, b])[2]
    assert "most allowed" in bad([many, a])
    assert len(json.loads(m.merge_boxes([many, many], True))) == 1       # 64 identical boxes collapse to one
    out = m.SYLayoutBoxesMerge().run(boxes_1=a, boxes_2=a, drop_duplicates=True)
    assert out[1] == 1 and json.loads(out[0]) == json.loads(a)
    assert m.SYLayoutBoxesMerge.RETURN_TYPES == ("STRING", "INT", "STRING") and len(m.SYLayoutBoxesMerge.RETURN_NAMES) == 3
    opt = list(m.SYLayoutBoxesMerge.INPUT_TYPES()["optional"])
    assert opt[:4] == ["boxes_1", "boxes_2", "boxes_3", "boxes_4"] and opt[-1] == "drop_duplicates" and len(opt) == 9
    return 38
