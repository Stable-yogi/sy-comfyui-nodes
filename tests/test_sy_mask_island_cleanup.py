import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_mask_island_cleanup as m


def _raises(fn, *args, word=""):
    try:
        fn(*args)
    except ValueError as e:
        return word in str(e)
    return False


def run():
    n = 0
    grid = [[1, 1, 0, 0],
            [1, 0, 0, 1],
            [0, 0, 0, 0]]
    labels, sizes = m.label_regions(grid)
    assert sorted(sizes) == [1, 3, 8]; n += 1
    assert sum(sizes) == 12; n += 1
    assert labels[0][0] == labels[0][1] == labels[1][0]; n += 1
    assert labels[0][2] != labels[0][0]; n += 1
    diag = [[1, 0], [0, 1]]
    assert sorted(m.label_regions(diag)[1]) == [1, 1, 1, 1]; n += 1      # diagonal pixels are not joined
    assert m.label_regions([[1]]) == ([[0]], [1]); n += 1               # smallest grid
    assert _raises(m.label_regions, [], word="empty"); n += 1
    assert _raises(m.label_regions, [[]], word="empty"); n += 1
    # speck removal and hole filling
    img = [[1] * 5 for _ in range(5)]
    img[2][2] = 0                                     # 1 pixel hole in a big white area
    out = m.clean_binary(img, 0, 2)
    assert out == [[1] * 5 for _ in range(5)]; n += 1
    img2 = [[0] * 5 for _ in range(5)]
    img2[2][2] = 1                                    # 1 pixel white speck
    assert m.clean_binary(img2, 2, 0) == [[0] * 5 for _ in range(5)]; n += 1
    assert m.clean_binary(img2, 1, 0) == img2; n += 1                   # speck of exactly the limit stays
    assert m.clean_binary(img, 0, 0) == img; n += 1                     # both limits 0 = identical
    assert m.clean_binary(img2, 0, 0) == img2; n += 1
    assert img[2][2] == 0; n += 1                                       # input untouched
    assert m.clean_binary([[1, 0]], 10000, 10000) in ([[0, 0]], [[1, 1]]); n += 1
    assert _raises(m.check_args, -1, 0, 0.5, word="min_island"); n += 1
    assert _raises(m.check_args, 0, 0, 1.5, word="threshold"); n += 1
    assert m.SYMaskIslandCleanup.RETURN_TYPES == ("MASK",); n += 1
    return n
