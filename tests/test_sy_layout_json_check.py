import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_layout_json_check as m
from _sy_layout import check_layout, MAX_BOXES, MAX_LABEL


def box(x=0, y=0, w=100, h=100, **extra):
    d = {"x": x, "y": y, "w": w, "h": h}
    d.update(extra)
    return d


def chk(boxes, cw=1000, ch=800, overlap=True):
    text = boxes if isinstance(boxes, str) else json.dumps(boxes)
    return check_layout(text, cw, ch, overlap)


def run():
    n = 0

    def expect(ok, boxes, words, cw=1000, ch=800, overlap=True):
        nonlocal n
        valid, rep = chk(boxes, cw, ch, overlap)
        assert valid is ok, (boxes, rep)
        for w in words:
            assert w in rep, (w, rep)
        n += 1
        return rep

    # valid layouts
    rep = expect(True, [box()], ["VALID", "1 box fits", "1000x800"])
    assert "INVALID" not in rep
    expect(True, [box(0, 0, 500, 800), box(500, 0, 500, 800)], ["VALID", "2 boxes"])           # touching, full canvas
    expect(True, [box(10.5, 20.25, 30.5, 40.5)], ["VALID"])                                       # decimals
    expect(True, [box(label="sign", colour="red")], ["VALID"])
    expect(True, [box(label="x" * MAX_LABEL)], ["VALID"])                                         # label exactly at limit
    expect(True, [box(color="blue")], ["VALID"])                                                  # US spelling accepted

    # boundaries: exactly on the edge is fine, one pixel more is not
    expect(True, [box(900, 700, 100, 100)], ["VALID"])
    expect(False, [box(901, 700, 100, 100)], ["right edge", "1001", "1000 wide"])
    expect(False, [box(900, 701, 100, 100)], ["bottom edge", "801", "800 high"])
    expect(True, [box(0, 0, 1000, 800)], ["VALID"])
    expect(False, [box(0, 0, 1001, 800)], ["right edge"])
    expect(False, [box(0, 0, 1000, 801)], ["bottom edge"])
    expect(True, [box(0, 0, 1, 1)], ["VALID"])                                                    # smallest real box
    expect(True, [box(999, 799, 1, 1)], ["VALID"])                                                # last pixel
    expect(False, [box(1000, 0, 1, 1)], ["right edge"])
    expect(False, [box(-1, 0, 10, 10)], ["outside the canvas", "x=-1"])
    expect(False, [box(0, -0.5, 10, 10)], ["outside the canvas", "y=-0.5"])

    # zero or negative size
    expect(False, [box(w=0)], ["no size", "w=0"])
    expect(False, [box(h=0)], ["no size", "h=0"])
    expect(False, [box(w=-5)], ["no size", "w=-5"])
    expect(False, [box(w=0, h=0)], ["no size"])

    # bad JSON and bad structure
    expect(False, "", ["empty"])
    expect(False, "   \n ", ["empty"])
    expect(False, "{not json", ["not valid JSON"])
    expect(False, "[{\"x\": 1,}]", ["not valid JSON"])
    expect(False, "{\"x\": 0, \"y\": 0, \"w\": 5, \"h\": 5}", ["list of boxes"])               # single object, not a list
    expect(False, "42", ["list of boxes"])
    expect(False, "\"text\"", ["list of boxes"])
    expect(False, "[]", ["no boxes"])
    expect(False, "[1]", ["box 1 is not an object"])
    expect(False, [box(), "text"], ["box 2 is not an object"])
    expect(False, [None], ["box 1 is not an object"])
    expect(False, [[1, 2, 3, 4]], ["box 1 is not an object"])

    # missing keys, one report line per key
    rep = expect(False, [{"x": 0, "y": 0, "w": 10}], ['missing "h"'])
    rep = expect(False, [{}], ['missing "x"', 'missing "y"', 'missing "w"', 'missing "h"', "4 problems"])
    expect(False, [{"y": 0, "w": 10, "h": 10}], ['missing "x"', "1 problem found"])

    # wrong types
    expect(False, [box(x="10")], ['"x" must be a number'])
    expect(False, [box(w=None)], ['"w" must be a number'])
    expect(False, [box(h=True)], ['"h" must be a number'])                                       # booleans are not numbers
    expect(False, [box(y=[1])], ['"y" must be a number'])
    expect(False, "[{\"x\": NaN, \"y\": 0, \"w\": 5, \"h\": 5}]", ['"x" must be a number'])
    expect(False, "[{\"x\": 0, \"y\": 0, \"w\": Infinity, \"h\": 5}]", ['"w" must be a number'])

    # labels
    expect(False, [box(label="x" * (MAX_LABEL + 1))], ["label is %d characters" % (MAX_LABEL + 1)])
    expect(False, [box(label=5)], ["label must be text"])

    # unknown colour is a warning only
    rep = expect(True, [box(colour="mauve")], ["VALID", "WARNING", "unknown colour"])
    expect(True, [box(colour=7)], ["WARNING", "unknown colour"])

    # several problems in several boxes are all reported, with the right box number and label
    rep = expect(False, [box(label="a"), box(5000, 0, 10, 10, label="far"), box(w=0, label="flat")],
                 ["2 problems", 'box 2 ("far")', 'box 3 ("flat")', "right edge", "no size"])
    assert "box 1" not in rep

    # overlap warnings
    rep = expect(True, [box(0, 0, 100, 100, label="a"), box(50, 50, 100, 100, label="b")], ["VALID", "WARNING", 'box 1 ("a") and box 2 ("b") overlap'])
    rep = expect(True, [box(0, 0, 100, 100), box(100, 0, 100, 100)], ["VALID"])                    # touching edges: no overlap
    assert "WARNING" not in rep
    rep = expect(True, [box(0, 0, 100, 100), box(99, 0, 100, 100)], ["WARNING", "overlap"])        # one pixel in
    rep = expect(True, [box(0, 0, 100, 100), box(50, 50, 100, 100)], ["VALID"], overlap=False)
    assert "WARNING" not in rep
    rep = expect(True, [box(0, 0, 500, 500), box(10, 10, 20, 20)], ["overlap"])                    # one inside another
    rep = expect(False, [box(0, 0, 100, 100), box(50, 50, w=0)], ["no size"])
    assert "overlap" not in rep                                                                   # broken box is not compared

    # box count limit
    many = [box(i, 0, 1, 1) for i in range(MAX_BOXES)]
    expect(True, many, ["VALID", "%d boxes" % MAX_BOXES], cw=2000, overlap=False)
    expect(False, many + [box(70, 0, 1, 1)], ["%d boxes; the most allowed is %d" % (MAX_BOXES + 1, MAX_BOXES)], cw=2000)

    # canvas size itself must make sense
    for bad in ((0, 100), (100, 0), (-1, 5), ("a", 5), (None, 5)):
        try:
            check_layout(json.dumps([box()]), bad[0], bad[1])
            raise SystemExit("bad canvas must raise")
        except ValueError:
            pass
        n += 1
    # the small canvas still tests boundaries
    expect(True, [box(0, 0, 1, 1)], ["VALID"], cw=1, ch=1)
    expect(False, [box(0, 0, 2, 1)], ["right edge"], cw=1, ch=1)

    # the node wrapper returns valid, report and the text unchanged
    text = json.dumps([box()])
    v, r, t = m.SYLayoutJsonCheck().run(text, 1000, 800, True)
    assert v is True and r.startswith("VALID") and t == text
    v, r, t = m.SYLayoutJsonCheck().run("nope", 1000, 800, True)
    assert v is False and r.startswith("INVALID")
    assert m.SYLayoutJsonCheck.RETURN_TYPES == ("BOOLEAN", "STRING", "STRING")
    return n + 5
