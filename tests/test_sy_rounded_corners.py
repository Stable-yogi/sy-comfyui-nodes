import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_rounded_corners as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def near(a, b, eps=1e-9):
    return abs(a - b) < eps


def run():
    n = 0
    # radius 0: everything inside
    assert m.corner_coverage(0, 0, 10, 10, 0) == 1.0; n += 1
    assert m.corner_coverage(9, 9, 10, 10, 0) == 1.0; n += 1
    # corner pixel is cut away, the centre is kept
    assert m.corner_coverage(0, 0, 100, 100, 30) == 0.0; n += 1
    assert m.corner_coverage(50, 50, 100, 100, 30) == 1.0; n += 1
    # straight edges away from corners stay fully covered
    assert m.corner_coverage(0, 50, 100, 100, 30) == 1.0; n += 1
    assert m.corner_coverage(50, 0, 100, 100, 30) == 1.0; n += 1
    # four corners are symmetric
    c = [m.corner_coverage(x, y, 100, 80, 20) for x, y in ((2, 2), (97, 2), (2, 77), (97, 77))]
    assert all(near(v, c[0]) for v in c); n += 1
    # soft edge: some pixels are strictly between 0 and 1
    vals = [m.corner_coverage(x, 0, 100, 100, 30) for x in range(0, 30)]
    assert any(0.0 < v < 1.0 for v in vals); n += 1
    # coverage never decreases walking in from the corner along the top row
    assert all(vals[i] <= vals[i + 1] + 1e-12 for i in range(len(vals) - 1)); n += 1
    # a pill / circle: radius capped at half of the shorter side
    assert m.corner_coverage(0, 0, 100, 40, 500) == 0.0; n += 1
    assert m.corner_coverage(50, 20, 100, 40, 500) == 1.0; n += 1
    assert near(m.corner_coverage(10, 10, 100, 40, 500), m.corner_coverage(10, 10, 100, 40, 20)); n += 1
    # circle: pixel on the horizontal middle line at the very left is inside the half-covered edge
    assert 0.0 < m.corner_coverage(0, 49, 100, 100, 50) <= 1.0; n += 1
    # 1x1 picture
    assert m.corner_coverage(0, 0, 1, 1, 0) == 1.0; n += 1
    assert 0.0 <= m.corner_coverage(0, 0, 1, 1, 5) <= 1.0; n += 1
    # 1xN strip does not crash and stays in range
    assert all(0.0 <= m.corner_coverage(0, y, 1, 20, 3) <= 1.0 for y in range(20)); n += 1
    # percent to pixels
    assert near(m.radius_pixels(10.0, 200, 100), 10.0); n += 1
    assert near(m.radius_pixels(50.0, 200, 100), 50.0); n += 1
    # bad input
    assert raises(m.corner_coverage, 0, 0, 0, 10, 1); n += 1
    assert raises(m.corner_coverage, 0, 0, 10, 10, -1); n += 1
    assert raises(m.radius_pixels, 51.0, 10, 10); n += 1
    assert raises(m.radius_pixels, -1.0, 10, 10); n += 1
    assert m.DEFAULT_BACKGROUND == "#000000"; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYRoundedCorners"] == "Rounded Corners SY"; n += 1
    return n
