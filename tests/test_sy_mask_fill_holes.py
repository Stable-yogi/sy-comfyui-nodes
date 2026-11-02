import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_fill_holes as m


def _raises(fn, *args, word=""):
    try:
        fn(*args)
    except ValueError as e:
        return word in str(e)
    return False


def run():
    n = 0
    ring = [[0] * 5 for _ in range(5)]
    for y in range(1, 4):
        for x in range(1, 4):
            ring[y][x] = 1
    ring[2][2] = 0
    assert m.label_holes(ring, "4") == [1]; n += 1                        # closed ring: one hole of 1 pixel
    assert m.label_holes(ring, "8") == [1]; n += 1
    gap = [r[:] for r in ring]
    gap[1][2] = 0                                                         # open the wall at the top
    gap[0][2] = 0
    assert m.label_holes(gap, "4") == []; n += 1                          # leaks out: no hole
    assert m.label_holes(gap, "8") == []; n += 1
    diag = [[0, 1, 0, 0],
            [1, 0, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0]]
    assert m.label_holes(diag, "4") == [1]; n += 1                        # diamond with a diagonal wall: shut for 4
    assert m.label_holes(diag, "8") == []; n += 1                         # leaks for 8
    two = [[0] * 9,
           [0, 1, 1, 1, 1, 1, 1, 1, 0],
           [0, 1, 0, 1, 0, 0, 1, 1, 0],
           [0, 1, 1, 1, 1, 1, 1, 1, 0],
           [0] * 9]
    assert sorted(m.label_holes(two, "4")) == [1, 2]; n += 1              # two holes of different size
    assert m.label_holes([[1]], "4") == []; n += 1
    assert m.label_holes([[0, 0], [0, 0]], "4") == []; n += 1             # all background reaches the border
    assert m.label_holes([[1, 1, 1], [1, 1, 1], [1, 1, 1]], "8") == []; n += 1
    assert len(m.hole_points(ring, "4")) == 1; n += 1
    assert len(m.sparse_components([(0, 0), (0, 1), (5, 5)], "4")) == 2; n += 1
    assert len(m.sparse_components([(0, 0), (1, 1)], "4")) == 2; n += 1
    assert len(m.sparse_components([(0, 0), (1, 1)], "8")) == 1; n += 1
    assert ring[2][2] == 0; n += 1                                        # input untouched
    assert _raises(m.label_holes, [], "4", word="empty"); n += 1
    assert _raises(m.check_args, 1.5, 0, "4", word="threshold"); n += 1
    assert _raises(m.check_args, 0.5, -1, "4", word="max_hole_size"); n += 1
    assert _raises(m.check_args, 0.5, 0, "6", word="connectivity"); n += 1
    assert m.SYMaskFillHoles.RETURN_TYPES == ("MASK",); n += 1
    return n
