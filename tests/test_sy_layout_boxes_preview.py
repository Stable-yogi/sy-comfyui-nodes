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
    # new: numbered plan, skipped boxes, info, tint and numbers
    two = json.dumps([dict(b, label="in"), dict(b, x=500, label="out"), dict(b, x=50, label="in2")])
    plan, skipped = m.plan_numbered(two, 100, 100)
    assert skipped == [2] and [p[3] for p in plan] == [1, 3] and [p[2] for p in plan] == ["in", "in2"]
    assert m.plan_boxes(two, 100, 100) == [p[:3] for p in plan]       # old function gives the same without numbers
    assert m.preview_info(2, [2], 100, 80) == "Drew 2 boxes on 100x80. Not drawn because they are fully outside the picture: box 2."
    assert m.preview_info(1, [], 64, 64) == "Drew 1 box on 64x64."
    assert m.preview_info(0, [1, 4], 8, 8).endswith("box 1, 4.")
    try:
        from PIL import Image
    except ImportError:
        Image = None
    if Image is not None:
        def px(img, xy):
            return img.getpixel(xy)
        base = (40, 40, 44)
        pl = m.plan_boxes(json.dumps([dict(b, colour="blue")]), 100, 100)
        flat = m.draw_plan(Image.new("RGB", (100, 100), base), pl, 1, False)
        assert px(flat, (25, 40)) == base                                # inside stays untouched by default
        assert px(flat, (10, 40)) == COLOUR_RGB["blue"]                  # outline drawn
        tint = m.draw_plan(Image.new("RGB", (100, 100), base), pl, 1, False, 0.5)
        assert px(tint, (25, 40)) != base and px(tint, (5, 5)) == base   # tinted inside only
        solid = m.draw_plan(Image.new("RGB", (100, 100), base), pl, 1, False, 1.0)
        assert px(solid, (25, 40)) == COLOUR_RGB["blue"]
        withnum = m.draw_plan(Image.new("RGB", (200, 200), base), m.plan_numbered(json.dumps([dict(b, y=60)]), 200, 200)[0], 1, False, 0.0, True)
        assert withnum.getbbox() is not None and px(withnum, (10, 80)) == COLOUR_RGB["red"]
        n_after = sum(1 for xy in [(x, y) for x in range(10, 40) for y in range(45, 60)] if px(withnum, xy) != base)
        assert n_after > 0                                               # number label painted above the box
    opt = m.SYLayoutBoxesPreview.INPUT_TYPES()["optional"]
    assert list(opt)[0] == "image" and "fill_opacity" in opt and "show_numbers" in opt
    assert m.SYLayoutBoxesPreview.RETURN_TYPES == ("IMAGE", "STRING") and len(m.SYLayoutBoxesPreview.RETURN_NAMES) == 2
    return 36
