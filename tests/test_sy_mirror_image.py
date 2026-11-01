import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mirror_image as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError as e:
        return str(e)
    return None


def apply(grid, mode):
    """Plain-list version of the node: grid is a list of rows."""
    rows_start, cols_start = m.mode_axes(mode)
    h, w = len(grid), len(grid[0])
    ri = m.axis_indices(h, rows_start) if rows_start is not None else list(range(h))
    ci = m.axis_indices(w, cols_start) if cols_start is not None else list(range(w))
    return [[grid[r][c] for c in ci] for r in ri]


def run():
    n = 0
    assert m.axis_indices(4, True) == [0, 1, 1, 0]; n += 1
    assert m.axis_indices(4, False) == [3, 2, 2, 3]; n += 1
    assert m.axis_indices(5, True) == [0, 1, 2, 1, 0]; n += 1
    assert m.axis_indices(5, False) == [4, 3, 2, 3, 4]; n += 1
    assert m.axis_indices(1, True) == [0] and m.axis_indices(1, False) == [0]; n += 1
    assert m.axis_indices(2, True) == [0, 0]; n += 1
    assert m.mirror_index(3, 4, True) == 0 and m.mirror_index(0, 4, False) == 3; n += 1
    g = [[1, 2, 3, 4], [5, 6, 7, 8]]
    assert apply(g, "left_to_right") == [[1, 2, 2, 1], [5, 6, 6, 5]]; n += 1
    assert apply(g, "right_to_left") == [[4, 3, 3, 4], [8, 7, 7, 8]]; n += 1
    assert apply(g, "top_to_bottom") == [[1, 2, 3, 4], [1, 2, 3, 4]]; n += 1
    assert apply(g, "bottom_to_top") == [[5, 6, 7, 8], [5, 6, 7, 8]]; n += 1
    assert apply(g, "four_way") == [[1, 2, 2, 1], [1, 2, 2, 1]]; n += 1
    odd = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    assert apply(odd, "left_to_right") == [[1, 2, 1], [4, 5, 4], [7, 8, 7]]; n += 1
    assert apply(odd, "four_way") == [[1, 2, 1], [4, 5, 4], [1, 2, 1]]; n += 1
    assert apply([[7]], "four_way") == [[7]]; n += 1
    assert apply([[1, 2, 3, 4, 5]], "right_to_left") == [[5, 4, 3, 4, 5]]; n += 1
    assert apply([[1], [2], [3]], "top_to_bottom") == [[1], [2], [1]]; n += 1
    msg = raises(m.mode_axes, "diagonal")
    assert msg and "mode" in msg; n += 1
    assert raises(m.mirror_index, 0, 0, True); n += 1
    assert raises(m.mirror_index, 4, 4, True); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYMirrorImage"] == "Mirror Image SY"; n += 1
    _k = [0]
    def _c(cond, msg="d3 check failed"):
        _k[0] += 1
        if not cond:
            raise AssertionError(msg)
    def _r(fn, *a):
        _k[0] += 1
        try:
            fn(*a)
        except ValueError as e:
            return str(e)
        raise AssertionError("expected ValueError for %r" % (a,))
    _c("left half onto the right" in m.mirror_info("left_to_right", 64, 32) and "odd" not in m.mirror_info("left_to_right", 64, 32))
    _c("middle column 32" in m.mirror_info("left_to_right", 65, 32) and "middle row" not in m.mirror_info("left_to_right", 65, 32))
    _c("middle column 2 and middle row 3" in m.mirror_info("four_way", 5, 7))
    _c("middle row 3" in m.mirror_info("top_to_bottom", 4, 7) and "middle column" not in m.mirror_info("top_to_bottom", 4, 7))
    _c("nothing changed" in m.mirror_info("left_to_right", 1, 9))
    for _mode in m.MODES:
        _c(len(m.mirror_info(_mode, 10, 10)) > 20)
    _r(m.mirror_info, "diagonal", 4, 4)
    _c(m.SYMirrorImage.RETURN_NAMES == ("image", "info"))
    return (n) + _k[0]
