import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_edge_detect as m


def raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def near(a, b, eps=1e-6):
    return abs(a - b) < eps


def run():
    n = 0
    assert near(m.luma(1, 1, 1), 1.0); n += 1
    assert near(m.luma(0, 0, 0), 0.0); n += 1
    assert near(m.luma(1, 0, 0), 0.2126) and near(m.luma(0, 1, 0), 0.7152) and near(m.luma(0, 0, 1), 0.0722); n += 1
    # convolution: identity kernel and replicate padding
    g = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    ident = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
    assert m.convolve_2d(g, ident) == g; n += 1
    ones = [[1, 1, 1]] * 3
    assert near(m.convolve_2d([[2.0]], ones)[0][0], 18.0); n += 1  # 1x1 grid: all 9 taps repeat the pixel
    assert raises(m.convolve_2d, g, [[1, 1], [1, 1]]); n += 1
    assert raises(m.convolve_2d, [], ident); n += 1
    # flat picture: no edges
    flat = [[0.5] * 4 for _ in range(4)]
    for method in m.METHODS:
        assert all(v == 0.0 for row in m.edge_map(flat, method, 1.0, False) for v in row); n += 1
    # vertical step 0 | 1: sobel is about 1 next to the step, 0 far away
    step = [[0.0, 0.0, 1.0, 1.0, 1.0] for _ in range(5)]
    e = m.edge_map(step, "sobel", 1.0, False)
    assert near(e[2][1], 0.5 * (1 + 2 + 1) / 4.0 * 2 / 2.0 * 1.0, 1e-9) or e[2][1] > 0.4; n += 1
    assert e[2][0] == 0.0 and e[2][4] == 0.0; n += 1
    assert near(e[2][1], e[2][2]); n += 1
    # invert
    inv = m.edge_map(step, "sobel", 1.0, True)
    assert near(inv[2][1], 1.0 - e[2][1]) and near(inv[2][0], 1.0); n += 1
    # laplacian on a single bright pixel
    dot = [[0.0] * 3 for _ in range(3)]
    dot[1][1] = 1.0
    lap = m.edge_map(dot, "laplacian", 1.0, False)
    assert near(lap[1][1], 1.0) and near(lap[0][1], 0.25) and lap[0][0] == 0.0; n += 1
    # strength scales and clamps
    assert near(m.edge_value("sobel", 0.4, 0.0, 1.0, False), 0.1); n += 1
    assert near(m.edge_value("sobel", 0.4, 0.0, 5.0, False), 0.5); n += 1
    assert m.edge_value("sobel", 4.0, 4.0, 10.0, False) == 1.0; n += 1
    # 1x1 and 1xN pictures work
    assert near(m.edge_map([[0.7]], "sobel", 1.0, False)[0][0], 0.0, 1e-9); n += 1
    assert len(m.edge_map([[0.0, 1.0, 0.0, 1.0]], "laplacian", 1.0, False)[0]) == 4; n += 1
    # bad input
    assert raises(m.edge_map, flat, "canny", 1.0, False); n += 1
    assert raises(m.edge_map, flat, "sobel", 0.0, False); n += 1
    assert raises(m.edge_map, flat, "sobel", 11.0, False); n += 1
    assert raises(m.edge_value, "bogus", 0, 0, 1.0, False); n += 1
    # node shape
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYEdgeDetect"] == "Edge Detect SY"; n += 1
    assert m.SYEdgeDetect.RETURN_TYPES == ("IMAGE", "MASK"); n += 1
    return n
