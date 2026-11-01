import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_image_grid as m

N = [0]


def ok(cond, msg="check failed"):
    N[0] += 1
    if not cond:
        raise AssertionError(msg)


def raises(fn, *args):
    N[0] += 1
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError("expected ValueError for %r" % (args,))


def run():
    lay = m.grid_layout(5, 3, 100, 50, 10, 0)
    ok(lay["rows"] == 2 and lay["columns"] == 3)
    ok(lay["width"] == 10 * 4 + 300 and lay["height"] == 10 * 3 + 100)
    ok(lay["cells"][0] == (10, 10, 60))
    ok(lay["cells"][1][0] == 120 and lay["cells"][3][:2] == (10, 70))
    lay2 = m.grid_layout(2, 8, 10, 10, 0, 12)
    ok(lay2["columns"] == 2 and lay2["width"] == 20 and lay2["height"] == 22)
    ok(lay2["cells"][1] == (10, 0, 10))
    raises(m.grid_layout, 0, 2, 10, 10, 1, 0)
    raises(m.grid_layout, 2, 0, 10, 10, 1, 0)
    raises(m.grid_layout, 2, 2, 10, 10, -1, 0)
    raises(m.grid_layout, 100, 100, 1000, 1000, 0, 0)
    ok(m.parse_color("black") == (0, 0, 0))
    ok(m.parse_color("#ff8000") == (255, 128, 0))
    ok(m.parse_color(" 00FF00 ") == (0, 255, 0))
    raises(m.parse_color, "banana")
    raises(m.parse_color, "12345")
    ok(m.text_color_for((0, 0, 0)) == (255, 255, 255))
    ok(m.text_color_for((255, 255, 255)) == (0, 0, 0))
    ok(m.split_labels("a\n b \nc", 2) == ["a", "b"])
    ok(m.split_labels("a", 3) == ["a", "", ""])
    ok(m.split_labels("", 2) == ["", ""])
    ok(m.label_height(["", ""], 20) == 0 and m.label_height(["x", ""], 20) == 28)
    ok(m.ab_columns(3, "row") == 3 and m.ab_columns(3, "column") == 1)
    raises(m.ab_columns, 3, "diagonal")
    ok(m.fit_inside_size(1000, 500, 512, 512) == (512, 256, 0, 128))
    ok(m.fit_inside_size(500, 1000, 512, 512) == (256, 512, 128, 0))
    ok(m.fit_inside_size(512, 512, 512, 512) == (512, 512, 0, 0))
    raises(m.fit_inside_size, 0, 5, 5, 5)
    ok(m.numbered_labels(3) == ["1", "2", "3"] and m.numbered_labels(0) == [])
    raises(m.check_fit, "zoom")
    ok(m.check_fit("keep shape") is None)
    lay3 = m.grid_layout(6, 3, 100, 50, 10, 0)
    t = m.sheet_info(6, lay3, 100, 50, 0, "stretch", False, 0)
    ok(t.startswith("Sheet of 6 picture(s): 3 column(s) x 2 row(s), cells 100x50, sheet 340x130") and t.endswith("."))
    ok("shape changed" in m.sheet_info(4, lay3, 100, 50, 2, "stretch", False, 0))
    ok("empty space" in m.sheet_info(4, lay3, 100, 50, 2, "keep shape", False, 0))
    ok("extra captions were ignored" in m.sheet_info(2, lay3, 100, 50, 0, "stretch", True, 5))
    ok("last ones have no caption" in m.sheet_info(5, lay3, 100, 50, 0, "stretch", True, 2))
    ok("caption" not in m.sheet_info(3, lay3, 100, 50, 0, "stretch", True, 3))
    ok(m.SYImageGrid.RETURN_NAMES == ("sheet", "info") and m.SYLabelledABGrid.RETURN_NAMES == ("strip", "info"))
    ok(list(m.SYImageGrid.INPUT_TYPES()["optional"]) == ["labels", "label_size", "fit", "auto_number"])
    ok(list(m.SYLabelledABGrid.INPUT_TYPES()["optional"])[-1] == "fit")
    return N[0]
