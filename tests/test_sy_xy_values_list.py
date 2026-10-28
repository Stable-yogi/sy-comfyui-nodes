import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_xy_values_list as m
import _sy_xy as h


def bad(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.make_list("numbers", 1, 7, 4, "", 0, 1, 1) == ("1\n3\n5\n7", 4); n += 1
    assert h.number_range(0, 1, 5) == ["0", "0.25", "0.5", "0.75", "1"]; n += 1
    assert h.number_range(7, 9, 1) == ["7"]; n += 1
    assert h.number_range(0, 1, 3) == ["0", "0.5", "1"]; n += 1
    assert h.number_range(5, 1, 3) == ["5", "3", "1"]; n += 1
    assert h.format_number(-0.0) == "0"; n += 1
    assert h.format_number(2.50) == "2.5"; n += 1
    assert m.make_list("text list", 0, 0, 1, " euler , ddim\n\nlms,", 0, 1, 1) == ("euler\nddim\nlms", 3); n += 1
    assert m.make_list("seeds", 0, 0, 1, "", 100, 3, 10) == ("100\n110\n120", 3); n += 1
    assert m.make_list("seeds", 0, 0, 1, "", 5, 3, 0) == ("5\n5\n5", 3); n += 1
    assert bad(m.make_list, "numbers", 0, 1, 0, "", 0, 1, 1); n += 1
    assert bad(m.make_list, "numbers", 0, 1, 65, "", 0, 1, 1); n += 1
    assert bad(m.make_list, "text list", 0, 1, 2, " , ,", 0, 1, 1); n += 1
    assert bad(m.make_list, "text list", 0, 1, 2, ",".join("a" * 1 for _ in range(65)), 0, 1, 1); n += 1
    assert bad(m.make_list, "seeds", 0, 1, 2, "", 1, 5, -1); n += 1
    assert bad(m.make_list, "seeds", 0, 1, 2, "", 1, 0, 1); n += 1
    assert bad(m.make_list, "colours", 0, 1, 2, "", 1, 1, 1); n += 1
    assert h.parse_axis("a\r\n b \n\n c") == ["a", "b", "c"]; n += 1
    assert h.parse_axis(None) == []; n += 1
    assert h.axis_sizes([], []) == (1, 1) and h.axis_sizes(["a", "b"], ["c"]) == (2, 1); n += 1
    assert h.pick_cell(3, 2, 4) == (1, 1); n += 1
    assert h.pick_cell(3, 2, 7, True) == (1, 0); n += 1
    assert bad(h.pick_cell, 3, 2, 6); n += 1
    assert bad(h.pick_cell, 3, 2, -1); n += 1
    assert h.parse_color("White") == (255, 255, 255) and h.parse_color("ff8000") == (255, 128, 0); n += 1
    assert bad(h.parse_color, "banana"); n += 1
    assert h.text_color_for((0, 0, 0)) == (255, 255, 255) and h.text_color_for((255, 255, 255)) == (0, 0, 0); n += 1
    lay = h.grid_layout(3, 2, 100, 50, 10, 5, 40, 20)
    assert lay["width"] == 5 + 40 + 10 + 300 + 20 + 5 and lay["height"] == 5 + 20 + 10 + 100 + 10 + 5; n += 1
    assert lay["cells"][0] == (55, 35) and lay["cells"][4] == (165, 95) and len(lay["cells"]) == 6; n += 1
    assert lay["col_x"][0] == 105.0 and lay["row_y"][1] == 120.0; n += 1
    lay = h.grid_layout(1, 1, 10, 10, 8, 0, 0, 0)
    assert (lay["width"], lay["height"], lay["cells"]) == (10, 10, [(0, 0)]); n += 1
    assert bad(h.grid_layout, 100, 1, 1000, 10, 0, 0, 0, 0); n += 1
    assert bad(h.grid_layout, 0, 1, 10, 10, 0, 0, 0, 0); n += 1
    assert bad(h.grid_layout, 1, 1, 10, 10, -1, 0, 0, 0); n += 1
    assert m.SYXYValuesList.RETURN_TYPES == ("STRING", "INT"); n += 1
    return n
