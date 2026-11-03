import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_layout_box_draw as m
from _sy_layout import COLOUR_NAMES, MAX_BOXES, check_layout


def refused(text, w=100, h=100, snap=1):
    try:
        m.draw_boxes_details(text, w, h, snap)
    except ValueError as e:
        return str(e)
    return None


def run():
    n = 0
    one = '[{"x": 10, "y": 20, "w": 30, "h": 40, "label": " sign ", "colour": "green"}]'
    text, info = m.draw_boxes_details(one, 100, 100)
    assert json.loads(text) == [{"x": 10, "y": 20, "w": 30, "h": 40, "label": "sign", "colour": "green"}]; n += 1
    assert info.startswith('1 box on a 100x100 canvas: "sign"'); n += 1
    # empty, blank and None are fine: nothing drawn yet
    for blank in ("", "   ", None, "[]"):
        t, i = m.draw_boxes_details(blank, 64, 64)
        assert t == "[]"; n += 1
    assert "Drag" in m.draw_boxes_details("", 64, 64)[1]; n += 1
    # missing colour: cycles through the palette; colour spelled "color" is accepted
    t, _ = m.draw_boxes_details('[{"x":0,"y":0,"w":5,"h":5},{"x":5,"y":5,"w":5,"h":5,"color":"blue"}]', 50, 50)
    d = json.loads(t)
    assert d[0]["colour"] == COLOUR_NAMES[0] and d[1]["colour"] == "blue"; n += 1
    assert d[0]["label"] == ""; n += 1
    # decimals are rounded to whole pixels
    d = json.loads(m.draw_boxes_details('[{"x":1.4,"y":2.6,"w":10.2,"h":9.5,"colour":"red"}]', 50, 50)[0])[0]
    assert (d["x"], d["y"], d["w"], d["h"]) == (1, 3, 10, 10); n += 1
    # snap
    d = json.loads(m.draw_boxes_details('[{"x":10,"y":21,"w":31,"h":39,"colour":"red"}]', 200, 200, 8)[0])[0]
    assert (d["x"], d["y"], d["w"], d["h"]) == (8, 24, 32, 40); n += 1
    # the output passes the layout checker (what Boxes Preview and Check read)
    ok, rep = check_layout(m.draw_boxes_details(one, 100, 100)[0], 100, 100)
    assert ok, rep; n += 1
    # largest allowed list
    many = json.dumps([{"x": i, "y": 0, "w": 1, "h": 1, "colour": "red"} for i in range(MAX_BOXES)])
    assert len(json.loads(m.draw_boxes_details(many, 200, 10)[0])) == MAX_BOXES; n += 1
    # refusals, each with plain words
    assert "most allowed" in refused(json.dumps([{"x": 0, "y": 0, "w": 1, "h": 1}] * (MAX_BOXES + 1))); n += 1
    assert "right edge" in refused('[{"x":90,"y":0,"w":20,"h":5,"colour":"red"}]'); n += 1
    assert "bottom edge" in refused('[{"x":0,"y":95,"w":5,"h":20,"colour":"red"}]'); n += 1
    assert "missing" in refused('[{"x":0,"y":0,"w":5}]'); n += 1
    assert "colour" in refused('[{"x":0,"y":0,"w":5,"h":5,"colour":"mauve"}]'); n += 1
    assert "bigger than 0" in refused('[{"x":0,"y":0,"w":0,"h":5,"colour":"red"}]'); n += 1
    assert "JSON" in refused("{not json"); n += 1
    assert refused('"text"') is not None; n += 1
    assert refused("[1, 2]") is not None; n += 1
    assert "canvas" in refused("[]", 0, 10); n += 1
    # the node class
    out = m.SYLayoutBoxDraw().run(100, 100, one, 1)
    assert out[0] == m.draw_boxes_details(one, 100, 100)[0] and out[2] == 1; n += 1
    assert m.SYLayoutBoxDraw().run(100, 100, "[]", 1)[2] == 0; n += 1
    assert m.SYLayoutBoxDraw.RETURN_NAMES == ("layout_boxes", "info", "box_count"); n += 1
    return n


if __name__ == "__main__":
    print("checks:", run())
