import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_perspective_warp as m

PLAIN = m.PLAIN_CORNERS


def _refuses(fn, word):
    try:
        fn()
    except ValueError as e:
        assert word in str(e), str(e)
        return 1
    raise SystemExit("expected ValueError")


def run():
    n = 0
    # normal: identity corners give the identity matrix
    h = m.homography_from_corners(PLAIN, PLAIN)
    for i in range(3):
        for j in range(3):
            assert abs(h[i][j] - (1.0 if i == j else 0.0)) < 1e-9
    n += 1
    # normal: each source corner lands on its target corner
    dst = [(0.1, 0.05), (0.9, 0.0), (1.0, 0.95), (0.0, 1.0)]
    h = m.homography_from_corners(PLAIN, dst)
    for s, d in zip(PLAIN, dst):
        x, y = m.apply_homography(h, *s)
        assert abs(x - d[0]) < 1e-9 and abs(y - d[1]) < 1e-9
    n += 1
    # round trip through the opposite matrix
    back = m.homography_from_corners(dst, PLAIN)
    x, y = m.apply_homography(back, *m.apply_homography(h, 0.3, 0.6))
    assert abs(x - 0.3) < 1e-9 and abs(y - 0.6) < 1e-9
    n += 1
    # a pure shift
    h = m.homography_from_corners(PLAIN, [(0.25, 0.5), (1.25, 0.5), (1.25, 1.5), (0.25, 1.5)])
    x, y = m.apply_homography(h, 0.5, 0.5)
    assert abs(x - 0.75) < 1e-9 and abs(y - 1.0) < 1e-9
    n += 1
    # edge: corners at the extremes still valid; plain corners accepted
    assert m.check_corners(PLAIN) == PLAIN
    m.check_corners([(-0.5, -0.5), (1.5, -0.5), (1.5, 1.5), (-0.5, 1.5)])
    assert m.is_plain(PLAIN) and not m.is_plain(dst)
    n += 3
    # output size
    assert m.output_size(100, 50, PLAIN, True)[:2] == (100, 50)
    assert m.output_size(100, 50, [(0.0, 0.0), (0.5, 0.0), (0.5, 0.5), (0.0, 0.5)], False)[:2] == (50, 25)
    n += 2
    # refusals: flipped, bow-tie, zero area, two corners the same, out of range
    n += _refuses(lambda: m.check_corners([(1, 0), (0, 0), (0, 1), (1, 1)]), "keep their order")
    n += _refuses(lambda: m.check_corners([(0, 0), (1, 1), (1, 0), (0, 1)]), "keep their order")
    n += _refuses(lambda: m.check_corners([(0, 0), (1, 0), (2, 0), (3, 0)]), "keep their order")
    n += _refuses(lambda: m.check_corners([(0, 0), (0, 0), (1, 1), (0, 1)]), "keep their order")
    n += _refuses(lambda: m.homography_from_corners([(0, 0), (1, 0), (2, 0), (3, 0)], PLAIN), "corners")
    n += _refuses(lambda: m.warp_tensor(None, PLAIN, "wrap", True), "edge")
    n += _refuses(lambda: m.warp_tensor(None, [(2.0, 0), (1, 0), (1, 1), (0, 1)], "black", True), "corner x")
    n += _refuses(lambda: m.output_size(8000, 8000, [(-0.5, -0.5), (1.5, -0.5), (1.5, 1.5), (-0.5, 1.5)], False), "keep_size")
    d = m.SYPerspectiveWarp.INPUT_TYPES()["required"]
    assert d["tl_x"][1]["default"] == 0.0 and d["br_x"][1]["default"] == 1.0 and d["keep_size"][1]["default"] is True
    n += 1
    return n
