import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_keep_largest as m


def _raises(fn, *args, word=""):
    try:
        fn(*args)
    except ValueError as e:
        return word in str(e)
    return False


def run():
    n = 0
    grid = [[1, 1, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0]]
    labels, sizes = m.label_components(grid, "8")
    assert sizes[0] == 13; n += 1                                         # background count
    assert sorted(sizes[1:]) == [2, 2, 3]; n += 1                         # diagonal pair joins for 8
    assert labels[2][2] == labels[3][3] != 0; n += 1
    assert labels[0][0] == labels[1][0] == labels[0][1]; n += 1
    assert sum(sizes) == 20; n += 1
    labels4, sizes4 = m.label_components(grid, "4")
    assert sorted(sizes4[1:]) == [1, 1, 2, 3]; n += 1                     # diagonal pair splits for 4
    assert labels4[2][2] != labels4[3][3]; n += 1
    u = [[1, 0, 1],
         [1, 1, 1]]
    assert sorted(m.label_components(u, "4")[1][1:]) == [5]; n += 1       # a U shape is one blob after merging
    assert m.label_components([[0]], "8") == ([[0]], [1]); n += 1
    assert m.label_components([[1]], "4") == ([[1]], [0, 1]); n += 1
    assert grid[0][0] == 1; n += 1                                        # input untouched
    assert m.pick_labels([13, 3, 2, 2], 1, 0) == [1]; n += 1
    assert m.pick_labels([13, 3, 2, 2], 2, 0) == [1, 2]; n += 1           # tie goes to the lower label
    assert m.pick_labels([13, 3, 2, 2], 3, 3) == [1]; n += 1              # min_pixels drops the small ones
    assert m.pick_labels([13, 3, 2, 2], 3, 8, scale=4) == [1, 2, 3]; n += 1
    assert m.pick_labels([5], 1, 0) == []; n += 1                         # nothing but background
    assert _raises(m.label_components, [], "8", word="empty"); n += 1
    assert _raises(m.label_components, [[1]], "5", word="connectivity"); n += 1
    assert _raises(m.check_args, 0.5, 0, 0, "8", word="keep"); n += 1
    assert _raises(m.check_args, 0.5, 17, 0, "8", word="keep"); n += 1
    assert _raises(m.check_args, 0.5, 1, -1, "8", word="min_pixels"); n += 1
    assert _raises(m.check_args, 2.0, 1, 0, "8", word="threshold"); n += 1
    assert m.SYMaskKeepLargest.RETURN_TYPES == ("MASK", "INT"); n += 1
    return n
