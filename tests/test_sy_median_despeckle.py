import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_median_despeckle as m


def _raises(fn, *args, word=""):
    try:
        fn(*args)
    except ValueError as e:
        return word in str(e)
    return False


def run():
    n = 0
    assert m.median_of_window([5]) == 5; n += 1
    assert m.median_of_window([9, 1, 5]) == 5; n += 1
    assert m.median_of_window([0.0, 1.0, 0.2, 0.1, 0.9]) == 0.2; n += 1
    assert m.median_of_window([3, 3, 3, 3, 100, 0, 3, 3, 3]) == 3; n += 1      # hot pixel ignored
    assert m.median_of_window([1, 2, 3, 4]) == 2; n += 1                        # even: lower middle
    assert _raises(m.median_of_window, [], word="empty"); n += 1
    flat = [[0.5] * 4 for _ in range(4)]
    assert m.median_filter_2d(flat, 3) == flat; n += 1
    speck = [[0.0] * 5 for _ in range(5)]
    speck[2][2] = 1.0
    assert m.median_filter_2d(speck, 3) == [[0.0] * 5 for _ in range(5)]; n += 1   # speck removed
    edge = [[0.0, 0.0, 1.0, 1.0] for _ in range(4)]
    assert m.median_filter_2d(edge, 3) == edge; n += 1                             # edge kept
    assert m.median_filter_2d([[7]], 15) == [[7]]; n += 1                          # 1x1, biggest window
    assert _raises(m.check_args, 4, 1, word="odd"); n += 1
    assert _raises(m.check_args, 17, 1, word="odd"); n += 1
    assert _raises(m.check_args, 3, 5, word="passes"); n += 1
    assert _raises(m.check_args, 3, 0, word="passes"); n += 1
    m.check_args(15, 4); n += 1
    assert m.SYMedianDespeckle.RETURN_TYPES == ("IMAGE",); n += 1
    return n
