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
    # new: info, snap_to, canvas check
    text, info = m.layout_box_details(10, 20, 300, 400, "sign", "green")
    assert info == 'Box "sign": 300x400 at (10, 20), right edge 310, bottom edge 420, green.'
    assert m.layout_box_details(0, 0, 5, 5, "", "red")[1].startswith("Box: 5x5")
    d = json.loads(m.layout_box_text(10, 21, 301, 399, "s", "red", 0, 0, 8))[0]
    assert (d["x"], d["y"], d["w"], d["h"]) == (8, 24, 304, 400)
    assert "Snapped to multiples of 8 (was x=10, y=21, w=301, h=399)" in m.layout_box_details(10, 21, 301, 399, "s", "red", 0, 0, 8)[1]
    d = json.loads(m.layout_box_text(0, 0, 3, 2, "tiny", "red", 0, 0, 64))[0]
    assert (d["w"], d["h"]) == (64, 64)                                  # never snaps to zero size
    assert "Snapped" not in m.layout_box_details(64, 128, 64, 64, "ok", "red", 0, 0, 64)[1]
    assert json.loads(m.layout_box_text(0, 0, 5, 5, "a", "red", 0, 0, 1))[0]["w"] == 5   # 1 = off
    assert json.loads(m.layout_box_text(900, 700, 100, 100, "e", "red", 1000, 800))[0]["x"] == 900   # exactly on the edge is fine
    for args, words in (((901, 0, 100, 100, "e", "red", 1000, 800), ("right edge", "1001", "1000 wide")),
                        ((0, 701, 100, 100, "e", "red", 1000, 800), ("bottom edge", "801", "800 high"))):
        try:
            m.layout_box_text(*args)
            raise SystemExit("must raise for %r" % (args,))
        except ValueError as e:
            assert all(w in str(e) for w in words) and 'Box "e"' in str(e), str(e)
    assert json.loads(m.layout_box_text(5000, 0, 100, 100, "free", "red", 0, 800))[0]["x"] == 5000   # 0 = no check on that side
    try:
        m.layout_box_text(0, 0, 0, 5, "a", "red", 100, 100, 8)           # bad numbers are refused before snapping
        raise SystemExit("must raise")
    except ValueError:
        pass
    out = m.SYLayoutBox().run(1, 2, 3, 4, "q", "cyan", 100, 100, 1)
    assert len(out) == 2 and out[1].startswith('Box "q"')
    assert m.SYLayoutBox.RETURN_TYPES == ("STRING", "STRING") and len(m.SYLayoutBox.RETURN_NAMES) == 2
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYLayoutBox"] == "Layout Box SY"
    return 31 + len(COLOUR_NAMES)
